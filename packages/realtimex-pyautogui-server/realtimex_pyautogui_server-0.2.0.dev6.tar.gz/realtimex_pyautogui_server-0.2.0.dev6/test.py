import time

# import pytesseract
import pyautogui

# Wait 3 seconds before starting (so you can switch to the browser)
print("You have 3 seconds to switch to your browser window...")
time.sleep(3)

start_time = time.time()
poll_interval = 1.0
timeout = 10

location = pyautogui.locateOnScreen("./elements/imessages/image.png", confidence=0.8)

if location:
    center = pyautogui.center(location)
    pyautogui.moveTo(center.x, center.y, duration=2)
    print("Found image at:", location)
else:
    print("Image not found on the screen.")

print("End time in second", time.time() - start_time)