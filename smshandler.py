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
from configparser import ConfigParser

modem = ""
client = mqtt.Client()
config = ConfigParser()

phonebook = {}

def SendSms(to, text):
    # Print log screen
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " Sending:   " + text)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " Recipient: " + to)
    print("===")

    # Send the sms via modem
    modem.sendSms(to, text)

def on_mqtt_connect(client, userdata, flags, rc):
    # Print status message and subscribe to sms topic
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

    # Print log to screen
    print(u'== SMS message received ==')
    print(u'From...: ' + str(smsFrom))
    print(u'Time...: ' + str(sms.time))
    print(u'Message: ' + str(sms.text))

    # Send sms contents to MQTT
    client.publish('/smsreceived', u'{"from":"' + smsFrom + '","datetime":"' + str(sms.time) + '","text":"' + sms.text + '"}')

    # Respond to sender if receipts are configured
    if config.getboolean('modem', 'receipt'):
        print('Replying to SMS...')
        sms.reply(u'SMS received: "{0}{1}"'.format(sms.text[:20], '...' if len(sms.text) > 20 else ''))
        print('SMS sent.')
    
    print('===')

def main():
    global modem
    global phonebook

    config.read('config.ini')

    # Create the phonebook
    tmpPhonebook = config.items('phonebook')
    for row in tmpPhonebook:
        phonebook[row[0]] = row[1]

    # Initialize the modem
    print('Initializing modem...')
    modem = GsmModem(config.get('modem', 'port'), config.getint('modem', 'baudrate'), smsReceivedCallbackFunc=on_gsm_handleSms)
    modem.smsTextMode = True

    # Connect to the modem
    try:
        modem.connect(config.get('modem', 'pin'))
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

    client.username_pw_set(config.get('mqtt', 'user'), config.get('mqtt', 'pass'))
    client.connect(config.get('mqtt', 'server'), config.getint('mqtt', 'port'), 60)

    client.loop_start()

    # Keep running forever
    try:
        modem.rxThread.join(2**31) # Specify a (huge) timeout so that it essentially blocks indefinitely, but still receives CTRL+C interrupt signal
    finally:
        modem.close()

if __name__ == '__main__':
    main()
