#!/usr/bin/python3

import pygame
import pygame.camera
from pygame.locals import *
import os
from PIL import Image
#import antigravity
import time
import shlex, subprocess

pygame.init()
pygame.camera.init()

#resolution = (640,480)
resolution = (1280,720)
#resolution = (1600,1200)
(maxX, maxY) = resolution
(x,y) = (0,0)

averageItems = 50
averageIndex = -1

lineSurface = pygame.surface.Surface((maxX,1))
lineSurfArray = pygame.surfarray.array3d(lineSurface)

intArray = [[0]*3]*maxX

averageArraySurface = pygame.surface.Surface((maxX,averageItems))
averageArray = pygame.surfarray.array3d(averageArraySurface)

showAverage = False
noAverage = False
yDisplayRow = -1

# read calibration file
calib = open("spectralCalibration.csv","r")
calibration = calib.read()
calib.close()

lcd = pygame.display.set_mode(resolution)

cam = pygame.camera.Camera("/dev/video2",resolution)
cam.start()

#subprocess.call(shlex.split('uvcdynctrl --set="Power Line Frequency" 0'))

image = cam.get_image()

print ("starting loop...")

going = True
while going:
	events = pygame.event.get()
	for e in events:
		if (e.type == MOUSEBUTTONDOWN):
			# get mouse position, averaging line
			(x,y) = pygame.mouse.get_pos()
			print(x,y)

		if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
#			cam.stop()
			going = False
		
		if (e.type == KEYUP and e.key == K_SPACE):
			showAverage = not showAverage
		if (e.type == KEYUP and e.key == K_a):
			noAverage = not noAverage

		if (e.type == KEYUP and e.key == K_KP_ENTER):
			timestr = time.strftime("%Y%m%d-%H%M%S")

			name = input("Name: ")
			desc = input("Description: ")

			# write time averaged image (integer average, 8-bits/color)
			fileName = "./%s-spectrum-%s.jpg" % (name,timestr)
			pygame.image.save(lcd, fileName)

			# write time averaged CSV, floating-point averaged colors
			fileName = "./%s-spectrum-%s.csv" % (name,timestr)
			f = open(fileName, "x")
			f.write( "%s,%s,%s\n" % (calibration.strip(),name,desc) )


			# each column
			for xCol in range (maxX):
				iTotal = 0
				# average over time
				for yRow in range(averageItems):
					# average the colors
					for zColor in range(3):
						iTotal += int(averageArray[xCol,yRow,zColor])

				f.write("%d,%f\n" % (xCol,iTotal/(3.0*averageItems)) )
			f.close()


	if cam.query_image():
		image = cam.get_image()

		averageIndex += 1
		if averageIndex >= averageItems:
			averageIndex = 0

		averageArray[0:maxX,averageIndex] = pygame.surfarray.array3d(image)[0:maxX,y]

		if showAverage :
			# average the columns
			for xCol in range(maxX):
				for zColor in range(3):
					iTotal = 0
					for yRow in range(averageItems):
						iTotal += int(averageArray[xCol,yRow,zColor])
					lineSurfArray[xCol,0,zColor] = iTotal/averageItems
						
			# what does it look like without averaging?
			if noAverage:
				lineSurfArray[0:maxX,0] = averageArray[0:maxX,averageIndex]

			# convert lineSurfArray to lineSurface
			lineSurface = pygame.surfarray.make_surface(lineSurfArray)
			# fill lcd with lineSurface
			for yIncr in range (averageItems):
				yDisplayRow += 1
				if yDisplayRow >= maxY:
					yDisplayRow = 0
				lcd.blit(lineSurface, (0,yDisplayRow))

		else:
			lcd.blit(image, (0,0))
			pygame.draw.line(lcd, (255,0,0), (0,y), (maxX,y), 1)

		pygame.display.flip()


