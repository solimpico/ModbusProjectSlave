#!/usr/bin/env python
# -*-coding:iso-8859-15-*-

# ---------------------------------------------------------------------------#
# import the modbus libraries we need
# ---------------------------------------------------------------------------#
from pymodbus.server.asynchronous import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer
import RPi.GPIO as GPIO
import time as t

# ---------------------------------------------------------------------------#
# import the twisted libraries we need
# ---------------------------------------------------------------------------#
from twisted.internet.task import LoopingCall

# ---------------------------------------------------------------------------#
# configure the service logging
# ---------------------------------------------------------------------------#
import logging

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# ---------------------------------------------------------------------------#
# DHT sensor configuration
# ---------------------------------------------------------------------------#
import sys
import Adafruit_DHT

sensor = Adafruit_DHT.DHT11
pin = 4

# VARIABILI MOTORINO
# define the pins connected to L293D
motoRPin1 = 27
motoRPin2 = 17
enablePin = 22


# _________________________________________________________________________________________
# CONTROLLO MOTORE

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(motoRPin1, GPIO.OUT)  # set pins to OUTPUT mode
    GPIO.setup(motoRPin2, GPIO.OUT)
    GPIO.setup(enablePin, GPIO.OUT)
    global p
    p = GPIO.PWM(enablePin, 1000)  # creat PWM and set Frequence to 1KHz
    p.start(90)


def motor(ADC):
    GPIO.output(motoRPin1, GPIO.HIGH)  # motoRPin1 output HIHG level
    GPIO.output(motoRPin2, GPIO.LOW)  # motoRPin2 output LOW level


def destroy():  # stop motore
    GPIO.output(motoRPin1, GPIO.LOW)  # motoRPin1 output HIHG level
    GPIO.output(motoRPin2, GPIO.LOW)  # motoRPin2 output LOW level


def loop():  # per l'avvio del motore
    while True:
        motor(1000)


# _________________________________________________________________________________________


# ---------------------------------------------------------------------------#
# define your callback process
# ---------------------------------------------------------------------------#
def updating_writer(a):
    log.debug("updating the context")
    context = a[0]
    function = 3
    slave_id = 0x00
    addressToRead = 0x01
    values = context[slave_id].getValues(function, addressToRead, count=2)
    if values[0] == 1:
        print("Ho ricevuto il dato 1: Telemetry")
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        values[0] = int(temperature)
        values[1] = int(humidity)
        log.debug("new values: " + str(temperature))
        log.debug("new values: " + str(humidity))
        context[slave_id].setValues(function, addressToRead, values)

    addressToRead = 0x10
    values = context[slave_id].getValues(5, addressToRead, 1)
    if values[0] == True:
        print("Accendo il motorino")
        motor(1000)

    if values[0] == False:
        print("Spengo il motorino")
        destroy()

    # humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

    # Note that sometimes you won't get a reading and
    # the results will be null (because Linux can't
    # guarantee the timing of calls to read the sensor).
    # If this happens try again!
    # if humidity is None or temperature is None:
    #   print ('Temp=' + temperature + 'Humidity: ' + humidty)
    # if humidity is None or temperature is None:
    #   humidity, temperature = (0, 0)
    #  print ('Temp=' + temperature + 'Humidity: ' + humidty)
    # values   = [v + 1 for v in values]
    # values[0] = temperature
    # values[1] = humidity
    # value = [temperature]
    # log.debug("new values: " + str(temperature))
    # context[slave_id].setValues(register, address, value)


# ---------------------------------------------------------------------------#
# initialize your data store
# ---------------------------------------------------------------------------#
store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [1] * 100),
    co=ModbusSequentialDataBlock(0, [2] * 100),
    hr=ModbusSequentialDataBlock(0, [3] * 100),
    ir=ModbusSequentialDataBlock(0, [4] * 100))
context = ModbusServerContext(slaves=store, single=True)

# ---------------------------------------------------------------------------#
# initialize the server information
# ---------------------------------------------------------------------------#
identity = ModbusDeviceIdentification()
identity.VendorName = 'pymodbus'
identity.ProductCode = 'PM'
identity.VendorUrl = 'http://github.com/bashwork/pymodbus/'
identity.ProductName = 'pymodbus Server'
identity.ModelName = 'pymodbus Server'
identity.MajorMinorRevision = '1.0'

# ---------------------------------------------------------------------------#
# run the server you want
# ---------------------------------------------------------------------------#
time = 0  # delay
loop = LoopingCall(f=updating_writer, a=(context,))
setup()
destroy()
loop.start(time, now=False)  # initially delay by time
StartTcpServer(context, identity=identity, address=("192.168.1.52", 502))