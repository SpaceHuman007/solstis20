import time
import board
import neopixel

PIXEL_PIN = board.D12
NUM_PIXELS = 800

pixels = neopixel.NeoPixel(
    PIXEL_PIN,
    NUM_PIXELS,
    brightness=0.1,
    auto_write=False,
    pixel_order=neopixel.GRB
)

# clear strip
pixels.fill((0,0,0))
pixels.show()

print("LED range tester")
print("Enter start and end LED numbers (example: 5 25)")
print("Press ENTER to turn them off")
print("Type q to quit\n")

while True:
 
    user = input("Enter LED range: ")

    if user.lower() == "q":
        break

    try:
        start, end = map(int, user.split())
    except:
        print("Invalid input")
        continue

    # clear first
    pixels.fill((0,0,0))

    for i in range(start, end + 1):
        if 0 <= i < NUM_PIXELS:
            pixels[i] = (0,240,255)

    pixels.show()

    input("Press ENTER to turn off")
    
    pixels.fill((0,0,0))
    pixels.show()

print("Exiting")
pixels.fill((0,0,0))
pixels.show()   