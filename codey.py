import RPi.GPIO as GPIO
import time
import subprocess
import sys
import select

HALL_PIN = 17
SPEAKER_DEVICE = "plughw:2,0"

GPIO.setmode(GPIO.BCM)
GPIO.setup(HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("System running... waiting for magnet")
print("Press 'c' + Enter to quit")

# start camera preview continuously
camera = subprocess.Popen([
    "rpicam-hello",
    "--autofocus-mode=continuous",
    "-t", "0"
])

try:
    last_state = 1

    while True:
              state = GPIO.input(HALL_PIN)

        # magnet detected
        if state == 0 and last_state == 1:
            print("why hello there")

            time.sleep(2)

            subprocess.run([
                "aplay",
                "-D", SPEAKER_DEVICE,
                "sound.wav"
            ])

        last_state = state

        # check keyboard input
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.readline().strip()
            if key.lower() == "c":
                print("Shutting down program...")
                break

        time.sleep(0.1)

except KeyboardInterrupt:
    pass

GPIO.cleanup()
camera.terminate()

print("GPIO cleaned. Program exited.")