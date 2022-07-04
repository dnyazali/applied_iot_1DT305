from machine import Pin, I2C, deepsleep
from umqtt.simple import MQTTClient
from BME280 import BME280
import time
import network
import config
import json

"""
Global variables and initializations
"""
scl_pin = Pin(22)
sda_pin = Pin(21)
led_pin = Pin(25)
i2c = I2C(scl=scl_pin, sda=sda_pin, freq=50000)
bme = BME280(i2c=i2c, address=0x76)
led = Pin(25, Pin.OUT, Pin.PULL_DOWN)

"""
Helper functions
"""
def i2c_scan(i2c_bus, scl_pin, sda_pin):
    """
    Scans the i2c bus and prints all
    the connected/found devices
    """
    devices = i2c_bus.scan()
    for device in devices:
        print("[i2c] Found device on hex addr:", hex(device))

def wifi_connect(ssid, passwd):
    """
    Connect to the WiFi network
    Credentials are stores in config.py
    """
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, passwd)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

def mqtt_publish(client, topic, msg):
    """
    Helper function to convert json data to
    string in order to publish messages over MQTT
    """
    payload = json.dumps(msg)
    client.connect()
    client.publish(topic, payload)
    client.disconnect()

"""
Main function
"""
def main():

    """
    Start by init the system with the i2c bus,
    connect to the network and the MQTT broker
    """
    print("Initializing system...")
    i2c_scan(i2c, scl_pin, sda_pin)
    wifi_connect(ssid=config.WIFI_SSID, passwd=config.WIFI_PASS)
    client = MQTTClient("umqtt_client", server=config.MQTT_ADDR, port=config.MQTT_PORT,
                                    user=config.MQTT_USER, password=config.MQTT_PASS)

    while True:
        led.on() # Indicate system is alive and connected

        # Load each BME datapoint values into separate variables,
        # using strip to only store the raw floating point values
        bme_temp = bme.values[0].strip('C')     # BME280 Temperature
        bme_pres = bme.values[1].strip('hPa')   # BME280 Pressure
        bme_humi = bme.values[2].strip('%')     # BME280 Humidity

        # Store the BME data as a dict, convert the dict to
        # a string using json.dumps() in mqtt_pub()
        bme_data = {
           "temp": float(bme_temp),
           "humi": float(bme_humi),
           "pres": float(bme_pres)
        }
        mqtt_publish(client, "BME", bme_data)

        led.off() # Indicate system is going to sleep; i.e. no longer connected
        time.sleep_ms(50) # Stabilize for led to turn off before deep sleeping
        deepsleep(1800000) # Deepsleep for 30mins before transmitting again

"""
System begins; where all the magic starts...
"""
if __name__ == '__main__':
    main()
