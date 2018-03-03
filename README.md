# smshandler
Python script watching a MQTT topic and send msg to SMS

Could be used for sending notifications to sms from a home automation platform such as Home Asssitant etc.

Listens to topic /sms/

Dependencies:
pip3 install python-gsmmodem-new
pip3 install paho-mqtt

Set config parameters to tty for the modems serial interface as well as parameters needed for mqtt

To send a sms to a phonebook number:
1. Edit the phonebook dictionary and add names and numbers to all persons
2. Send a MQTT message to topic /sms/name

To send a sms to all numbers in phonebook 
1. Send a MQTT message to topic /sms/all

To send a sms to any number
1. Send a MQTT message to topic /sms/xxxxxxxxxxx
The number will be translated to +xxxxxxxxxxx, no plus sign in the topic
