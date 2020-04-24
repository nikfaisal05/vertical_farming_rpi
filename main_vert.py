#!/usr/bin/python

from __future__ import print_function

#import paho.mqtt.client as paho


import board
import neopixel
import time
import random
import Adafruit_DHT
from relay_lib_seeed import *
import datetime

import schedule
import os

broker = "broker.hivemq.com"
port = 1883


LED_NO = 120
pixels = neopixel.NeoPixel(board.D21, LED_NO)
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 8

start_pump1 = datetime.time(8, 2, 0)
end_pump1 = datetime.time(8, 3, 0)
start_pump2 = datetime.time(18, 0, 0)
end_pump2 = datetime.time(18, 1, 0)

start_off_led = datetime.time(0, 0, 0)
end_off_led = datetime.time(3, 0 ,0)


def mqtt_init():
    client1 = paho.Client("vert_farm_control")
    client1.on_publish = on_publish
    client1.connect(broker, port)
    ret = client1.publish("vert_farm/kzaman", "on")

def take_picture():
    os.system('fswebcam -r 1280x720 -S 3 --jpeg 50 --save /home/pi/vert_farm/cam/%Y-%m-%d_%H%M%S.jpg')

def get_humid_temp():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        print("Temp={0:0.1f}*C Humidity={1:0.1f}%".format(temperature, humidity))
    else: 
        print("Failed to retrieve data from humidity sensor")
        return None, None
    return humidity, temperature

def on_led():
    print("Led is on")
    for i in range(LED_NO):
        pixels[i] = (255, 255, 255)

def off_led():
    print("Led is off")
    for i in range(LED_NO):
        pixels[i] = (0, 0, 0)

def on_relay(relay_no):
    relay_on(relay_no)

def off_relay(relay_no):
    relay_off(relay_no)

def time_in_range(start, end, x):
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end
def on_publish(clent, userdata,result):
    pass

def process_loop():
    schedule.run_pending()
    current_time = datetime.datetime.now().time()

    get_humid_temp()

    if (time_in_range(start_off_led, end_off_led, current_time)):
        off_led()
    else:
        on_led()
    
    if time_in_range(start_pump1, end_pump1, current_time) or time_in_range(start_pump2, end_pump2, current_time):
        on_relay(1)
    else:
        off_relay(1)

    time.sleep(60)


if __name__ == "__main__":
    schedule.every(3).hours.do(take_picture)
    while True:
        try:
            process_loop()
        except KeyboardInterrupt:
            print("Exiting application")
            relay_all_off()
            off_led()
            sys.exit(0)



