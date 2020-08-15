#!/usr/bin/python3
# coding: utf-8

# SMS Handler v1.0, 2020
# Created by Peter Österberg, HexBit AB
# Question are directed to github
#
# Free for all to use, no responsibilities or warranties given
#

from __future__ import print_function

import time, logging, sys
import paho.mqtt.client as mqtt
from gsmmodem.modem import GsmModem

### User defined settings

PORT = '/dev/ttyUSB1'   # Set to tty that the GSM modem is connected to
BAUDRATE = 115200       # Set to GSM modem's baud rate, normally 115200baud
PIN = 0000              # Set to SIM card's PIN #
RECEIPT = True          # Set to True to send a receipt back when SMS is received, set to False to do nothing

MQTTSERVER = "hassio"    # Set to host/ip that the MQTT server is running on
MQTTPORT = 1883             # Set to port that the MQTT server is listening on
MQTTUSER = "user"       # Set to MQTT username
MQTTPASS = "pass"       # Set to MQTT password

phonebook = {"name1":"+46XXXXXXXXX", "name2":"+45XXXXXXXXXX"}    # Phonebook example, pairs of name and phonenumber

### End of user defined settings

modem = ""
client = mqtt.Client()

def SendSms(to, text):
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " Sending:   " + text)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " Recipient: " + to)
    print("===")
    modem.sendSms(to, text)

def on_mqtt_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("/sms/#")

def on_mqtt_message(client, userdata, msg):
    destination = msg.topic[5:]
    smsText = msg.payload.decode("utf-8")

    if destination.isdigit():
        destination = "+" + destination
        SendSms(destination, smsText)
    elif destination == 'all':
        for person in phonebook.keys():
            SendSms(phonebook[person], smsText)
    elif destination in phonebook.keys():
        SendSms(phonebook[destination], smsText)
    else:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " Unknown recipient")

def on_gsm_handleSms(sms):
    smsFrom = sms.number

    # Find name in dictionary
    if smsFrom in phonebook.values():
        for key in phonebook.keys():
            if smsFrom == phonebook[key]:
                smsFrom = key

    print(u'== SMS message received ==')
    print(u'From...: ' + str(smsFrom))
    print(u'Time...: ' + str(sms.time))
    print(u'Message: ' + str(sms.text))

    client.publish('/smsreceived', u'{"from":"' + smsFrom + '","datetime":"' + str(sms.time) + '","text":"' + sms.text + '"}')

    if RECEIPT:
        print('Replying to SMS...')
        sms.reply(u'SMS received: "{0}{1}"'.format(sms.text[:20], '...' if len(sms.text) > 20 else ''))
        print('SMS sent.')
    
    print('===')

def main():
    global modem
    print('Initializing modem...')

    # Uncomment the following line to see what the modem is doing:
    #logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    # Initialize the modem
    modem = GsmModem(PORT, BAUDRATE, smsReceivedCallbackFunc=on_gsm_handleSms)
    modem.smsTextMode = True

    print(PIN)
    try:
        modem.connect(PIN)
    except PinRequiredError:
        print('Pin required')
        sys.exit(1)
    except IncorrectPinError:
        print('Wrong pin')
        sys.exit(1)

    # Print information about modem and network
    print(u'Connected to modem: {0} {1}'.format(modem.manufacturer, modem.model))
    print(u'Connected to network: {0}'.format(modem.networkName))
    print(u'Signal strenght: {0}'.format(str(modem.signalStrength)))
    print('Ready!')
    print('===')

    # Make sure to empty incoming sms bucket
    modem.processStoredSms()

    # Initialize MQTT
    client.on_connect = on_mqtt_connect
    client.on_message = on_mqtt_message

    client.username_pw_set(MQTTUSER, MQTTPASS)
    client.connect(MQTTSERVER, MQTTPORT, 60)

    client.loop_start()

    # Keep running forever
    try:
        modem.rxThread.join(2**31) # Specify a (huge) timeout so that it essentially blocks indefinitely, but still receives CTRL+C interrupt signal
    finally:
        modem.close()

if __name__ == '__main__':
    main()
