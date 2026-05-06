import time
import threading
import subprocess
import sys
import select
import signal

from gpiozero import Button
import board
import neopixel

# =========================
# PIN SETUP
# =========================
HALL_PIN = 24          # hall effect sensor signal
BUTTON_PIN = 23        # push button signal
PIXEL_PIN = board.D12  # LED strip signal on GPIO12

# =========================
# DEVICES / SETTINGS
# =========================
SPEAKER_DEVICE = "plughw:2,0"
SOUND_FILE = "sound.wav"

NUM_PIXELS = 795
LED_COUNT_ON_PRESS = 20
LED_BRIGHTNESS = 0.10
LED_COLOR = (0, 240, 255)

HALL_BOUNCE_TIME = 0.2
BUTTON_BOUNCE_TIME = 0.05
HALL_RETRIGGER_DELAY = 2.0   # prevents repeated sound spam while magnet stays near

# =========================
# GLOBAL STATE
# =========================
running = True
camera_process = None
last_hall_trigger_time = 0
state_lock = threading.Lock()

# =========================
# LED SETUP
# =========================
pixels = neopixel.NeoPixel(
    PIXEL_PIN,
    NUM_PIXELS,
    brightness=LED_BRIGHTNESS,
    auto_write=False,
    pixel_order=neopixel.GRB
)

def clear_leds():
    pixels.fill((0, 0, 0))
    pixels.show()

def set_last_20_leds_on():
    clear_leds()
    # Calculate starting point (e.g., 800 - 20 = 780)
    start_index = max(0, NUM_PIXELS - LED_COUNT_ON_PRESS)
    
    for i in range(start_index, NUM_PIXELS):
        pixels[i] = LED_COLOR
    pixels.show()

# =========================
# CAMERA
# =========================
def start_camera():
    global camera_process
    try:
        camera_process = subprocess.Popen([
            "rpicam-hello",
            "--autofocus-mode", "continuous",
            "-t", "0"
        ])
        print("Camera preview started.")
    except Exception as e:
        print(f"Could not start camera: {e}")

def stop_camera():
    global camera_process
    if camera_process is not None:
        try:
            camera_process.terminate()
            camera_process.wait(timeout=3)
            print("Camera stopped.")
        except subprocess.TimeoutExpired:
            camera_process.kill()
            print("Camera force-killed.")
        except Exception as e:
            print(f"Error stopping camera: {e}")
        finally:
            camera_process = None

# =========================
# SOUND
# =========================
def play_sound():
    try:
        subprocess.run(
            ["aplay", "-D", SPEAKER_DEVICE, SOUND_FILE],
            check=False
        )
    except Exception as e:
        print(f"Error playing sound: {e}")

def hall_triggered():
    global last_hall_trigger_time

    now = time.time()
    with state_lock:
        if now - last_hall_trigger_time < HALL_RETRIGGER_DELAY:
            return
        last_hall_trigger_time = now

    print("Hall sensor triggered.")
    threading.Thread(target=play_sound, daemon=True).start()

# =========================
# BUTTON LED CALLBACKS
# =========================
def button_pressed():
    print(f"Button pressed: turning on last {LED_COUNT_ON_PRESS} LEDs.")
    set_last_20_leds_on()

def button_released():
    print("Button released: turning off LEDs.")
    clear_leds()

# =========================
# CLEAN SHUTDOWN
# =========================
def shutdown():
    global running
    if not running:
        return

    running = False
    print("\nShutting down...")
    clear_leds()
    stop_camera()

def signal_handler(sig, frame):
    shutdown()

# =========================
# MAIN
# =========================
def main():
    global running

    print("Starting system...")
    clear_leds()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    hall_sensor = Button(
        HALL_PIN,
        pull_up=True,
        bounce_time=HALL_BOUNCE_TIME
    )

    button = Button(
        BUTTON_PIN,
        pull_up=True,
        bounce_time=BUTTON_BOUNCE_TIME
    )

    # Hall sensor: active when pulled LOW
    hall_sensor.when_pressed = hall_triggered

    # Button: LEDs on while held
    button.when_pressed = button_pressed
    button.when_released = button_released

    start_camera()

    print("System running.")
    print("Hall sensor on GPIO24")
    print("Button on GPIO23")
    print("LEDs on GPIO12")
    print("Press Ctrl+C to quit, or type q then Enter.\n")

    try:
        while running:
            if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
                user_input = sys.stdin.readline().strip().lower()
                if user_input == "q":
                    shutdown()
                    break

            time.sleep(0.05)

    except KeyboardInterrupt:
        shutdown()
    finally:
        clear_leds()
        print("Program exited cleanly.")

if __name__ == "__main__":
    main()