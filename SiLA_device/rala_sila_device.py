#!/usr/bin/env python
# -*- coding: utf-8 -*-

#_____________________________________________________________________________
#
# PROJECT: LARA
# CLASS: SiLAprocessManager
# FILENAME: lara_sila_process_manager.py
#
# CATEGORY:
#
# AUTHOR: mark doerr
# EMAIL: mark@ismeralda.org
#
# VERSION: 0.0.3
#
# CREATION_DATE: 2014/09/19
# LASTMODIFICATION_DATE: 2014/09/20
#
# BRIEF_DESCRIPTION: SiLA compliant Reader device for Raspberry Pi
# DETAILED_DESCRIPTION:
#
# ____________________________________________________________________________
#
#   Copyright:
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This file is provided "AS IS" with NO WARRANTY OF ANY KIND,
#   INCLUDING THE WARRANTIES OF DESIGN, MERCHANTABILITY AND FITNESS FOR
#   A PARTICULAR PURPOSE.
#
#   For further Information see COPYING file that comes with this distribution.
#_______________________________________________________________________________


import logging

from pysimplesoap.server import SoapDispatcher, SOAPHandler
from BaseHTTPServer import HTTPServer

import RPi.GPIO as GPIO
#~ import GPIO_dummy as GPIO
import time

# blinking function
def blink(num, blink_delay, pin):
	for i in range(0,num): 
		GPIO.output(pin,GPIO.HIGH)
		time.sleep(blink_delay)
		GPIO.output(pin,GPIO.LOW)
		time.sleep(blink_delay)
	return

class SiLADevice(object):
	green_LED = 16
	red_LED = 18
	blue_LED = 22
	def __init__(self):
		print("!!! please switch dummy off ... !!!!!")		
		sila_namespace = "http://sila-standard.org"
		
		dispatcher = SoapDispatcher( 'LARASiLADevice',
						location = "http://localhost:8008/",
						action = 'http://localhost:8008/', # SOAPAction
						namespace = sila_namespace,
						trace = True,
						ns = True )
		
		# register the user function
		dispatcher.register_function('GetStatus', self.get_status,
									 returns={'Status': int}, 
									 args={'requestID': str} )
									 			
		dispatcher.register_function('GetDeviceIdentification', self.get_device_identification,
									 returns={'SiLA_DeviceClass': int, "DeviceName": str }, 
									 args={'requestID': str} )
									 
		dispatcher.register_function('Initialize', self.initialize,
									 returns={'Status': int}, 
									 args={'requestID': str} )
									 
		dispatcher.register_function('Reset', self.reset,
									 returns={'Status': int}, 
									 args={'requestID': str} )

		dispatcher.register_function('Abort', self.abort,
									 returns={'standardResponse': int}, 
									 args={'requestID': str} )

		dispatcher.register_function('Pause', self.pause,
									 returns={'standardResponse': int}, 
									 args={'requestID': str} )
									 
		dispatcher.register_function('DoContinue', self.doContinue,
									 returns={'Status': int}, 
									 args={'requestID': str} )

		dispatcher.register_function('LockDevice', self.lockDevice,
									 returns={'Status': int}, 
									 args={'requestID': str} )									 

		dispatcher.register_function('UnlockDevice', self.unlockDevice,
									 returns={'Status': int}, 
									 args={'requestID': str} )	
									 
		dispatcher.register_function('OpenDoor', self.openDoor,
									 returns={ }, 
									 args={'requestID': int, 'lockID': str } )

		dispatcher.register_function('CloseDoor', self.closeDoor,
									 returns={ }, 
									 args={'requestID': int, 'lockID': str } )
			
		dispatcher.register_function('ExecuteMethod', self.executeMethod,
									 returns={'complexResponse':[] }, 
									 args={'requestID': int, 'lockID': str, 'methodName':str,'priority':int  } )
		
		print "Starting sila device soap server..."
		httpd = HTTPServer(("", 8008), SOAPHandler)
		httpd.dispatcher = dispatcher
		
		# blink to show "I am ready" 
		blink(3, 0.1, SiLADevice.green_LED)
		
		httpd.serve_forever()
		GPIO.cleanup()
			
	def get_device_identification(self, requestID):
		SiLA_reader_device = 4
		SiLA_DeviceIdentification = {}
		SiLA_DeviceIdentification["SiLA_DeviceClass"] = SiLA_reader_device
		SiLA_DeviceIdentification["DeviceName"] = "RasPiSiLADemoPlateReader"
		return(SiLA_DeviceIdentification)
		

	def get_status(self, requestID):
		if requestID == "LARASiLAPMS1":
			blink(6, 0.3, SiLADevice.green_LED)
			return(1)
		else :
			return(0)

	def initialize(self):
		pass

	def reset(self):
		pass
		
	def abort(self,requestID=0):
		pass
		
	# locking mechanism
	def lockDevice(self):
		pass

	def unlockDevice(self):
		pass
			
	def pause(self,requestID=0):
		pass

	def doContinue(self):
		pass
		
	# special commands
	def openDoor(self, requestID, lockID):
		for i in range(3):
			blink(1, 0.5, SiLADevice.green_LED)
			blink(1, 0.5, SiLADevice.blue_LED)
			blink(1, 0.5, SiLADevice.red_LED)
		
	def closeDoor(self, requestID, lockID):
		for i in range(3):
			blink(1, 0.5, SiLADevice.red_LED)
			blink(1, 0.5, SiLADevice.blue_LED)
			blink(1, 0.5, SiLADevice.green_LED)
			
	def executeMethod(self, requestID, lockID, methodName="", priority=10):
		logging.debug("Executing method %s on RaspPi demo Reader" % methodName)
		blink(10, 0.1, SiLADevice.blue_LED)
		result_array = [3.0, 6.7, 8.9]
		return(result_array)
			
if __name__ == "__main__":
	logging.basicConfig(format='%(levelname)s| %(module)s.%(funcName)s:%(message)s', level=logging.DEBUG)
	# to use Raspberry Pi board pin numbers
	GPIO.setmode(GPIO.BOARD)

	# set up GPIO output channel
	GPIO.setup(16, GPIO.OUT)
	GPIO.setup(18, GPIO.OUT)
	GPIO.setup(22, GPIO.OUT)

    #~ blink(3, 0.4, 18)
    	
	SiLADevice()
	
	#~ GPIO.cleanup()
