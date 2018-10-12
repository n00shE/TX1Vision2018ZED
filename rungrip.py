#!/usr/bin/python3

"""
Simple skeleton program for running an OpenCV pipeline generated by GRIP and using NetworkTables to send data.

Users need to:

1. Import the generated GRIP pipeline, which should be generated in the same directory as this file.
2. Set the network table server IP. This is usually the robots address (roborio-TEAM-frc.local) or localhost
3. Handle putting the generated code into NetworkTables
"""

import sys
import cv2
import numpy as np
import math
import urllib
import datetime
import os
import pyzed.camera as zcam
import pyzed.types as tp
import pyzed.core as core
import pyzed.defines as sl

from networktables import NetworkTables
from grip import GripPipeline  

def print_camera_information(cam):
	print("Resolution: {0}, {1}.".format(round(cam.get_resolution().width, 2), cam.get_resolution().height))
	print("Camera FPS: {0}.".format(cam.get_camera_fps()))
	print("Firmware: {0}.".format(cam.get_camera_information().firmware_version))
	print("Serial number: {0}.".format(cam.get_camera_information().serial_number))

print("Running...")
streamRunning = True
init = zcam.PyInitParameters()
init.camera_resolution = sl.PyRESOLUTION.PyRESOLUTION_HD720
init.camera_fps = 15
cam = zcam.PyZEDCamera()
runtime = zcam.PyRuntimeParameters()
if not cam.is_opened():
	print("Opening ZED Camera...")
status = cam.open(init)
if status != tp.PyERROR_CODE.PySUCCESS:
	print(repr(status))
	streamRunning = False
	exit()
err = cam.grab(runtime)
if err == tp.PyERROR_CODE.PySUCCESS:
	streamRunning = True

mat = core.PyMat()

print_camera_information(cam)

now = datetime.datetime.now()
print("Vision Log for " + str(now.day) + "/" + str(now.month) + "/" + str(now.year) + "  ~    " + str(now.hour) + ":" + str(now.minute) +":" + str(now.second))
print("OpenCV version: " + str(cv2.__version__))
print("Starting Vision...")

bytes = ''
version = int(cv2.__version__[:1])
pipeline = GripPipeline()

try:
    NetworkTables.setTeam(2551) 
    NetworkTables.setIPAddress("roborio-2551-frc.local")
    NetworkTables.setClientMode()
    NetworkTables.initialize()
    print("Initializing Network Tables...")
except:
    print("Network Tables already initialized")
    pass

#NetworkTable.setTeam(2551) 
#NetworkTable.setIPAddress("roborio-2551-frc.local")
#NetworkTable.setClientMode()
#NetworkTable.initialize()
#print("Initializing Network Tables...")

sd = NetworkTables.getTable('GRIP/myContoursReport')

#cap = cv2.VideoCapture(0)
"""
try:
	stream = urllib.urlopen("http://localhost:1180/?action=stream")
except:
	streamRunning = False

if streamRunning:
	print("Stream ONLINE")
	print("VISION SYSTEM ONLINE")
else:
	print("Stream OFFLINE")
	print("FATAL ERROR")
"""


"""
while(streamRunning == True):
   # Capture frame-by-frame  
	ret, frame = cap.read()
	if ret:
		# Display the resulting frame    
		cv2.imshow('Frame', frame)
		pipeline.process(frame)
		print pipeline.boundingRects
		print pipeline.center

    # Press Q on keyboard to  exit
	if cv2.waitKey(25) & 0xFF == ord('q'):
		break
 
   #Break the loop
	else: 
		break
"""

while streamRunning:
	cam.retrieve_image(mat, sl.PyVIEW.PyVIEW_LEFT)
	cv2.imshow("ZED", mat.get_data())
	#bytes += stream.read(1024)
	#a = bytes.find('\xff\xd8')
	#b = bytes.find('\xff\xd9')
	#if a != -1 and b != -1:
		#jpg = bytes[a:b+2]
		#bytes = bytes[b+2:]

		#color = cv2.CV_LOAD_IMAGE_COLOR if version == 2 else cv2.IMREAD_COLOR #name better
		#frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), color)

		#cv2.imshow('Image', frame)

	pipeline.process(mat.get_data())
		#print pipeline.boundingRects
		#print pipeline.center
		#print pipeline.filter_contours_output
		#print pipeline.rects
		#print pipeline.largestRect
	if (pipeline.largestRect) != None: 
		"""
		#xtwo = pipeline.rects[0][0] + pipeline.rects[0][2]
		#ytwo = pipeline.rects[0][1] + pipeline.rects[0][3]
		#cv2.rectangle(frame, (pipeline.rects[0][0],pipeline.rects[0][1]), (xtwo,ytwo), (255,0,0), thickness=3, lineType=8, shift=0)
		#cv2.imshow("Rectangle", frame)
		"""
		xtwo = pipeline.largestRect[0] + pipeline.largestRect[2]
		ytwo = pipeline.largestRect[1] + pipeline.largestRect[3]
	    
		centerX = [pipeline.largestRect[0] + pipeline.largestRect[2]/2]
		centerY = [pipeline.largestRect[1] + pipeline.largestRect[3]/2]
		cv2.rectangle(mat.get_data(), (pipeline.largestRect[0],pipeline.largestRect[1]), (xtwo,ytwo), (255,0,0), thickness=3, lineType=8, shift=0)
		cv2.imshow("Rectangle", mat.get_data())

		sd.putNumberArray("centerX", centerX)
		sd.putNumberArray("centerY", centerY)
		sd.putNumberArray("width", [pipeline.largestRect[2]])
		sd.putNumberArray("height", [pipeline.largestRect[3]])
		sd.putNumberArray("area", [pipeline.largestArea])
#		sd.putNumber("Test", len(pipeline.largestRect))
#		print pipeline.largestArea
	else:
		sd.putNumberArray("centerX", [])
		sd.putNumberArray("centerY", [])
		sd.putNumberArray("width", [])
		sd.putNumberArray("height", [])
		sd.putNumberArray("area", [])


		# Press Q on keyboard to  exit
	if cv2.waitKey(25) & 0xFF == ord('q'):
		cam.close()
		break
   
