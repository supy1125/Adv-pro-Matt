import os, sys, io
import M5
from M5 import *
from hardware import *
import time
import math

# Setup variables for the display and IMU
title0 = None
label3 = None  # Label for displaying burned calories

imu_val = None
last_imu_val = [0, 0, 0]
burned_calories = 0.0

# Initialize the RGB LED strip
rgb2 = None

# Define LED colors for different calorie burn intervals
calories_colors = [
    (10, (255, 0, 0)),       # 0-10
    (20, (255, 46, 0)),      # 10-20
    (30, (255, 77, 0)),      # 20-30
    (40, (255, 122, 0)),      # 30-40
    (50, (255, 150, 0)),     # 40-50
    (60, (255, 200, 0)),     # 50-60
    (70, (255, 245, 0)),     # 60-70
    (80, (204, 255, 0)),     # 70-80
    (90, (170, 255, 0)),     # 80-90
    (100, (60, 255, 0)),     # 90-100
]

r = 255
r_final = 0
g = 0
g_final = 255
b = 0
b_final = 0


def setup():
    global title0, label3, rgb2

    M5.begin()
    title0 = Widgets.Title("Calorie Tracker", 3, 0x000000, 0xffffff, Widgets.FONTS.DejaVu18)
    label3 = Widgets.Label("Burn: 0.0", 3, 20, 1.0, 0xffffff, 0x000000, Widgets.FONTS.DejaVu18)  # Updated label text to "Burn"

    # Initialize the RGB LED strip
    rgb2 = RGB(io=2, n=30, type="SK6812")  # Confirm the correct GPIO pin and LED type
    update_rgb_colors(burned_calories)  # Initialize LED strip color

def update_rgb_colors(calories):
    global rgb2, calories_colors
    global r_final, g_final, b_final
    for threshold, color in calories_colors:
        if calories <= threshold:
            r_final = color[0]
            g_final = color[1]
            b_final = color[2]
            #rgb_color = (color[0] << 16) | (color[1] << 8) | color[2]
            #rgb2.fill_color(rgb_color)
            break

def loop():
    global label3
    global imu_val, last_imu_val, burned_calories
    global r, g, b, r_final, g_final, b_final
    M5.update()
  
    # Read IMU accelerometer values
    imu_val = Imu.getAccel()
  
    # Detect movement based on acceleration change
    if abs(imu_val[0] - last_imu_val[0]) > 0.2 or abs(imu_val[1] - last_imu_val[1]) > 0.2 or abs(imu_val[2] - last_imu_val[2]) > 0.2:
        burned_calories += 0.1
        label3.setText("Burn: {:.1f}".format(burned_calories))  # Update the displayed burned calories
        update_rgb_colors(burned_calories)
  
    # Update last_imu_val for the next iteration
    last_imu_val = imu_val
  
    if r < r_final:
        r += 1
    elif r > r_final:
        r -= 1
    if g < g_final:
        g += 1
    elif g > g_final:
        g -= 1
    if b < b_final:
        b += 1
    elif b > b_final:
        b -= 1
    
    color = (r << 16) | (g << 8) | b
    rgb2.fill_color(color)
    time.sleep_ms(10)

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
      print("please update to latest firmware")