#!/usr/bin/python3
print("test a")
import RPi.GPIO as GPIO
from time import *
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(26,GPIO.IN)
GPIO.setup(23,GPIO.OUT)
GPIO.setup(24,GPIO.OUT)
GPIO.setup(25,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)
GPIO.setup(20,GPIO.OUT)

def clear():
    for i in range(48):
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21,GPIO.LOW)
        GPIO.output(21,GPIO.HIGH)
    GPIO.output(22,GPIO.LOW)
    GPIO.output(22,GPIO.HIGH)
    GPIO.output(23,GPIO.LOW)
    GPIO.output(24,GPIO.LOW)
    GPIO.output(25,GPIO.LOW)

def sw():
    for i in range(48):
        if i < counter:
            GPIO.output(20, GPIO.HIGH)
        else:
            GPIO.output(20, GPIO.LOW)
        GPIO.output(21,GPIO.LOW)
        GPIO.output(21,GPIO.HIGH)
    GPIO.output(22,GPIO.LOW)
    GPIO.output(22,GPIO.HIGH)
    GPIO.output(23,GPIO.LOW)
    GPIO.output(24,GPIO.LOW)
    GPIO.output(25,GPIO.LOW)
    
counter = 0
clear()
while(True):
    clicked=GPIO.input(26)
    if clicked==0:
        sw()
        if counter == 48:
            counter = 0
            clear()
        counter += 1
    sleep(0.5)