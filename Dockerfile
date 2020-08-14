FROM python:2
ADD smshandler.py /
RUN pip install paho-mqtt python-gsmmodem-new
CMD [ "python", "./smshandler.py" ]