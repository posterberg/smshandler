# smshandler
Python script watching a MQTT topic and send msg to SMS

Could be used for sending notifications to sms from a home automation platform such as Home Asssitant etc.

Listens to topic /sms/

### Dependencies:
pip3 install python-gsmmodem-new paho-mqtt

Set config parameters to tty for the modems serial interface as well as parameters needed for mqtt

## To send a sms to a phonebook number:
1. Edit the phonebook dictionary and add names and numbers to all persons
2. Send a MQTT message to topic /sms/name

## To send a sms to all numbers in phonebook 
1. Send a MQTT message to topic /sms/all

## To send a sms to any number
1. Send a MQTT message to topic /sms/xxxxxxxxxxx
The number will be translated to +xxxxxxxxxxx, no plus sign in the topic

## Receive sms 
Messages can also be received. Received messages will be sent to the MQTT topic '/smsreceived' on the format `b'{"from":"+NUMBER","datetime":"2020-08-14 18:44:52+02:00","text":"Sms message"}'`. +NUMBER will be replaced by a name if the NUMBER is available in the phonebook.


## Docker
A docker file provided to build a docker image.

Run `docker build -t smshandler .` to create a docker image.
Run `docker run smshandler` to start a docker container from the image.