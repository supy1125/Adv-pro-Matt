import M5
from machine import Pin
import time
import random

# 初始化全局变量
start_time = 0
pin1 = None

def pin_callback(pin):
    global start_time
    if start_time > 0:  # 确保计时已经开始
        end_time = time.ticks_ms()
        reaction_time_ms = end_time - start_time  # 直接使用毫秒
        M5.Lcd.fillScreen(0xffffff)  # 清屏为白色
        M5.Lcd.setTextColor(0x000000)  # 设置文字颜色为黑色
        M5.Lcd.setTextSize(3)  # 设置字体大小，数字越大字体越大
        # 假设M5.Lcd.print仅接受一个字符串参数，使用默认位置
        M5.Lcd.print("Reaction Time: {} ms".format(reaction_time_ms))
        start_time = 0  # 重置开始时间

def setup():
    global pin1
    M5.begin()
    M5.Lcd.fillScreen(0xff0000)  # 初始屏幕颜色设置为红色
    pin1 = Pin(1, mode=Pin.IN, pull=Pin.PULL_UP)
    pin1.irq(trigger=Pin.IRQ_FALLING, handler=pin_callback)

def loop():
    global start_time
    wait_time = random.randint(1, 5)
    time.sleep(wait_time)
    start_time = time.ticks_ms()
    M5.Lcd.fillScreen(0x75ff5c)  # 将屏幕变为绿色

if __name__ == '__main__':
    try:
        setup()
        while True:
            loop()
            time.sleep(10)  # 给用户一些时间阅读结果
    except Exception as e:
        print("Error:", e)
