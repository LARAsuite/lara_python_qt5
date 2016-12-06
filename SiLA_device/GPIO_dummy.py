#!/usr/bin/env python
# -*- coding: utf-8 -*-

# just a dummy class to capture RaspBerry Pi GPio calls ....

import logging


HIGH, LOW, OUT, BOARD = range(4) 

def output(pin,state=LOW):
    if state == LOW:
        logging.info("pin: %i :blink off" % pin)
    
    if state == HIGH:
        logging.info("pin: %i :blink on" % pin)
        
def output(pin,state=LOW):
    logging.info("setting pin %i to state %i" % (pin, state))

def setup(pin,state=LOW):
    logging.info("setting up pin %i to state %i" % (pin, state))
        
def setmode(device):
    logging.info("setting Pi board %i" % device)
        
def cleanup():
    logging.info("cleaning GPIO up ...")
