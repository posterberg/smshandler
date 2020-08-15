FROM python:3
ADD smshandler.py /
ADD config.ini /
RUN pip3 install --upgrade pip
RUN pip3 install paho-mqtt python-gsmmodem-new
CMD [ "python3", "./smshandler.py" ]
