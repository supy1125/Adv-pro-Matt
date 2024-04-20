import os, sys, io
import M5
from M5 import *
from hardware import *
import time
import network
from umqtt.simple import MQTTClient
from servo import Servo

title0 = None
label0 = None
servo1 = None
servo2 = None
mqtt_client = None
aio_user_name = 'Supervan'
aio_password = 'aio_BCMX14dPN6ZohGxmAg4MHl7YfGXa'
adc1 = None
rgb2 = None

red = 0
red_final = 0
green = 0
green_final = 0

mqtt_timer = 0

adc_calibration_val = 2500

def wifi_connect():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect('IKUN DEHOUSE_', '55667788')
    print('Connecting to WiFi...', end='')
    while not wifi.isconnected():
        print('.', end='')
        time.sleep_ms(100)
    print('Connected. IP address:', wifi.ifconfig()[0])

def on_message(topic, msg):
    global servo1, servo2, adc1
    adc_val = adc1.read()  # Read ADC value immediately when message is received
    print("Topic: {}; Message: {}".format(topic, msg.decode('utf-8')))
    if topic == b'{}/feeds/Time-feed'.format(aio_user_name) and adc_val > adc_calibration_val:
        duration = int(msg)
        start_servo_and_rgb(duration)

def start_servo_and_rgb(duration):
    global servo1, servo2, rgb2
    time.sleep(5)  # Delay before starting the action
    global red_final, green_final
    steps = 100
    step_duration = duration / steps
    servo1.move(170)  # Move servos at the beginning of the color transition
    servo2.move(20)
    for i in range(steps):
        r = int(255 - (255 * (i / steps)))
        g = int(255 * (i / steps))
        rgb2.fill_color(get_color(r, g, 0))
        time.sleep(step_duration)
    #rgb2.fill_color(get_color(0, 255, 0))
    red_final = 0
    green_final = 255
    servo1.move(90)
    servo2.move(95)

def get_color(r, g, b):
    return (r << 16) | (g << 8) | b

def setup():
    global title0, label0, servo1, servo2, mqtt_client, adc1, rgb2
    global adc_calibration_val
    M5.begin()
    title0 = Widgets.Title("Servo Control via Adafruit IO", 3, 0x000000, 0xffffff, Widgets.FONTS.DejaVu18)
    label0 = Widgets.Label("---", 3, 20, 1.0, 0xffffff, 0x000000, Widgets.FONTS.DejaVu18)

    wifi_connect()

    servo1 = Servo(pin=38)
    servo2 = Servo(pin=7)
    servo1.move(90)
    servo2.move(95)

    #adc1 = ADC(Pin(1))
    adc1 = ADC(Pin(1), atten=ADC.ATTN_11DB)

    rgb2 = RGB(io=5, n=30, type="SK6812")

    mqtt_client = MQTTClient(client_id='m5stack', server='io.adafruit.com', user=aio_user_name, password=aio_password)
    mqtt_client.set_callback(on_message)
    mqtt_client.connect()
    mqtt_client.subscribe('{}/feeds/Time-feed'.format(aio_user_name))
    
    # make light calibration value a little bit higher than sensor value:
    #adc_calibration_val = adc1.read()
    #adc_calibration_val += 100
    print('adc_calibration_val =', adc_calibration_val)
    

def loop():
    global mqtt_client, adc1
    global red, red_final
    global green, green_final
    global mqtt_timer
    
    M5.update()
    adc_val = adc1.read()
    
    if adc_val <= adc_calibration_val:
        red_final = 0
        green_final = 0 
    else:
        red_final = 255
        
        #rgb2.fill_color(get_color(0, 0, 0))  # Turn off RGB when ADC value is low
    if(red < red_final):
        red += 1
    elif(red > red_final):
        red -= 1
    if(green < green_final):
        green += 1
    elif(green > green_final):
        green -= 1
        
    rgb2.fill_color(get_color(red, green, 0))
    time.sleep_ms(1)
            
    # check mqtt messages every 100 milliseconds:
    if(time.ticks_ms() > mqtt_timer + 100):
        mqtt_client.check_msg()
        mqtt_timer = time.ticks_ms()
        print('adc_val =', adc_val)
    #time.sleep_ms(100)

if __name__ == '__main__':
    try:
        setup()
        while True:
            loop()
    except (Exception, KeyboardInterrupt) as e:
        mqtt_client.disconnect()
        print('Disconnected from Adafruit IO')
        sys.print_exception(e)