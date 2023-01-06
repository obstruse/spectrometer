#!/usr/bin/python3

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import pygame.camera
from pygame.locals import *
from PIL import Image
#import antigravity
import time
import shlex, subprocess

from configparser import ConfigParser
import argparse

# change to the python directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# read config file, to override the default (fallback) settings
config = ConfigParser()
config.read('config.ini')
width = config.getint('Spectrometer','width',fallback=1280)
height = config.getint('Spectrometer','height',fallback=720)
videoDev = config.get('Spectrometer','videoDev',fallback='/dev/video0')
averageItems = config.getint('Spectrometer','averageItems',fallback=50)

# read command line, to override the config file settings
parser = argparse.ArgumentParser(description='Spectrometer')
parser.add_argument('-x','--width'     ,dest='width',default=width,type=int)
parser.add_argument('-y','--height'    ,dest='height',default=height,type=int)
parser.add_argument('-v','--video'     ,dest='videoDev',default=videoDev)

args = parser.parse_args()
width = args.width
height = args.height
videoDev = args.videoDev

pygame.init()
pygame.camera.init()

resolution = (width,height)
(x,y) = (0,0)

averageIndex = -1

lineSurface = pygame.surface.Surface((width,1))
lineSurfArray = pygame.surfarray.array3d(lineSurface)

intArray = [[0]*3]*width

averageArraySurface = pygame.surface.Surface((width,averageItems))
averageArray = pygame.surfarray.array3d(averageArraySurface)

showAverage = False
noAverage = False
yDisplayRow = -1

# read calibration file
try:
	calib = open("calibration.csv","r")
	calibration = calib.read()
	calib.close()
except:
	calibration = ",,436,611"

lcd = pygame.display.set_mode(resolution)

cam = pygame.camera.Camera(videoDev,resolution)
cam.start()

#subprocess.call(shlex.split('uvcdynctrl --set="Power Line Frequency" 0'))

image = cam.get_image()


active = True
while active:
	events = pygame.event.get()
	for e in events:
		if (e.type == MOUSEBUTTONDOWN):
			# get mouse position, averaging line
			(x,y) = pygame.mouse.get_pos()

		if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
#			cam.stop()
			active = False
		
		if (e.type == KEYUP and e.key == K_SPACE):
			showAverage = not showAverage
		if (e.type == KEYUP and e.key == K_a):
			noAverage = not noAverage

		if (e.type == KEYUP and (e.key == K_KP_ENTER or e.key == K_RETURN)):
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
			for xCol in range (width):
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
		averageIndex = averageIndex % averageItems

		averageArray[0:width,averageIndex] = pygame.surfarray.array3d(image)[0:width,y]

		if showAverage :
			# average the columns
			for xCol in range(width):
				for zColor in range(3):
					iTotal = 0
					for yRow in range(averageItems):
						iTotal += int(averageArray[xCol,yRow,zColor])
					lineSurfArray[xCol,0,zColor] = iTotal/averageItems
						
			# what does it look like without averaging?
			if noAverage:
				lineSurfArray[0:width,0] = averageArray[0:width,averageIndex]

			# convert lineSurfArray to lineSurface
			lineSurface = pygame.surfarray.make_surface(lineSurfArray)
			# fill lcd with lineSurface
			for yIncr in range (averageItems):
				yDisplayRow += 1
				yDisplayRow = yDisplayRow % height
				lcd.blit(lineSurface, (0,yDisplayRow))

		else:
			lcd.blit(image, (0,0))
			pygame.draw.line(lcd, (255,0,0), (0,y), (width,y), 1)

		pygame.display.flip()

cam.stop
