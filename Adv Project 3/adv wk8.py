import os, sys, io
import M5
from M5 import *
from hardware import *
import time
from servo import Servo
import random
from _thread import start_new_thread

title0 = None
label0 = None
servo1 = None
servo2 = None
adc1 = None
rgb2 = None
last_position = 90
servo1_moving = False

def setup():
    global title0, label0, servo1, servo2, adc1, rgb2
    M5.begin()
    title0 = Widgets.Title("ADC Servo Control", 3, 0x000000, 0xffffff, Widgets.FONTS.DejaVu18)
    label0 = Widgets.Label("--", 3, 20, 1.0, 0xffffff, 0x000000, Widgets.FONTS.DejaVu18)
    servo1 = Servo(pin=38)
    servo2 = Servo(pin=7)
    servo1.move(70)
    servo2.move(70)
    adc1 = ADC(Pin(1), atten=ADC.ATTN_11DB)
    rgb2 = RGB(io=5, n=30, type="SK6812")  # Initialize the RGB LED
    rgb2.fill_color(get_color(255, 0, 0))
    time.sleep(2)

def get_color(r, g, b):
  rgb_color = (r << 16) | (g << 8) | b
  return rgb_color

def set_led_color_to_red():
    global rgb2
    #rgb2.fill((255, 0, 0))
    rgb2.fill_color(get_color(255, 0, 0))

def set_led_color_to_green():
    global rgb2
    #rgb2.fill((0, 255, 0))
    rgb2.fill_color(get_color(0, 255, 0))

# def move_servo_randomly():
#     global servo_moving
#     servo_moving = True
#     set_led_color_to_red()  # Set LED to red when moving
#     random_delay = random.uniform(0, 5)
#     time.sleep(random_delay)
#     if last_position == 40:
#         servo.move(40)
#         time.sleep(1)
#         servo.move(90)
#         set_led_color_to_green()  # Change LED back to green
#     servo_moving = False

def move_servo_randomly():
    global servo1_moving
    servo1_moving = True
    random_delay = random.uniform(0, 5)  # Generate a random floating number between 0 and 5 seconds
    time.sleep(random_delay)  # Random delay
    if last_position == 40:  # Ensure the condition still satisfies after the delay
        servo1.move(70)
        servo2.move(70)
        time.sleep(0.3)
        servo1.move(90)
        servo2.move(90)
    servo1_moving = False

def loop():
    global label0, adc1, servo1, last_position, servo1_moving
    M5.update()
    adc1_val = adc1.read()  # Read light sensor value
    label0.setText(str(adc1_val))  # Display light sensor value
    

    if adc1_val > 3000 and last_position != 40: # and not servo_moving:
        # Use thread to start random movement to avoid blocking the main loop
        #start_new_thread(move_servo_randomly, ())
        last_position = 40  # Update position state
        move_servo_randomly()
        set_led_color_to_red()  
    elif adc1_val <= 3000 and last_position != 120: # and not servo_moving:
        # Light condition improved, move back to original position if servo is not moving randomly
        servo1.move(135)
        servo2.move(135)
        time.sleep(0.3)  # How long it moves
        # Stop servo:
        servo1.move(90)
        servo2.move(90)
        last_position = 120
        set_led_color_to_green()

    time.sleep(0.1)  # Short delay to debounce sensor reading and reduce loop speed

if __name__ == '__main__':
    try:
        setup()
        while True:
            loop()
    except (Exception, KeyboardInterrupt) as e:
        try:
            from utility import print_error_msg
            print_error_msg(e)
        except ImportError:
            print("Please update to latest firmware")

