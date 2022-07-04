from machine import Pin
from umqtt.simple import MQTTClient
import time
import network
import config
import json

"""
Global variables and port initializations
"""
rsw_pin = Pin(13)
rsw = Pin(13, Pin.OUT, Pin.PULL_DOWN)

"""
Helper functions
"""
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

def sub_cb(topic, msg):
    """
    Received messages from subscriptions
    will be delivered to this callback
    """

    # Decode msg in UTF-8 charset to parse
    # the data and act upon the message
    data = msg.decode('UTF-8')
    if data == 'rsw03_on':
        rsw.on()
        time.sleep_ms(50) # Stabilize
    elif data == 'rsw03_off':
        rsw.off()
        time.sleep_ms(50) # Stabilize
    else:
        rsw.off()
        time.sleep_ms(50) # Stabilize

"""
Main function
"""
def main():

    """
    Start by init the system with the i2c bus,
    connect to the network and the MQTT broker
    """
    print("Initializing system...")
    wifi_connect(ssid=config.WIFI_SSID, passwd=config.WIFI_PASS)
    client = MQTTClient("umqtt_client2", server=config.MQTT_ADDR, port=config.MQTT_PORT,
                                    user=config.MQTT_USER, password=config.MQTT_PASS)

    """
    Setup callback, connect to the
    MQTT broker and subscribe to 'AC'
    """
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe("AC")

    try:
        while True:
            client.wait_msg() # Blocking wait for message
            time.sleep_ms(50) # Stabilize
    finally:
        """
        Power off and disconnect if the
        system is ever in a faulty state
        """
        rsw.off()
        client.disconnect()

"""
System begins; where all the magic starts...
"""
if __name__ == '__main__':
    main()
