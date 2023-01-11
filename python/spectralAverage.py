#!/usr/bin/python3

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import pygame.camera
from pygame.locals import *
from PIL import Image
#import antigravity
import math
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
averageItems = config.getint('Spectrometer','averageItems',fallback=20)

# read command line, to override the config file settings
parser = argparse.ArgumentParser(description='Spectrometer')
parser.add_argument('-x','--width'     ,dest='width',default=width,type=int)
parser.add_argument('-y','--height'    ,dest='height',default=height,type=int)
parser.add_argument('-v','--video'     ,dest='videoDev',default=videoDev)
parser.add_argument('-a','--average'   ,dest='averageItems',default=averageItems,type=int)

args = parser.parse_args()
width = args.width
height = args.height
videoDev = args.videoDev
averageItems = args.averageItems

pygame.init()
pygame.camera.init()

font = pygame.font.Font(None, 24)

WHITE = (255,255,255)
BLACK = (0,0,0)

resolution = (width,height)
(x,y) = (0,0)

averageIndex = -1

# array to hold the lines to be averaged
averageArraySurface = pygame.surface.Surface((width,averageItems))
averageArray = pygame.surfarray.array3d(averageArraySurface)

# the average of the lines
lineSurface = pygame.surface.Surface((width,1))
lineSurfArray = pygame.surfarray.array3d(lineSurface)

# output surface, the averaged spectrum
outSurface = pygame.surface.Surface(resolution)
outSurface.fill(BLACK)
outSurface.set_colorkey(BLACK)

# Out Of Range surface
oorSurface = pygame.surface.Surface((width,1))
oorSurface.fill(BLACK)
oorSurface.set_colorkey(BLACK)

# text surface
txtSurface = pygame.surface.Surface(resolution)
txtSurface.fill(BLACK)
txtSurface.set_colorkey(BLACK)

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

DESC = { "name": "description", "pos":(width-10,10), "text":"description", "color":WHITE, "border":True }
TAG = { "name": "tag", "pos":(width-10,42), "text":"prefix", "color":WHITE, "border":True }
TXT = ( DESC, TAG)

txtActive = -1

#utility functions
def setV4L2( ctrl, value ) :
    return subprocess.run(shlex.split(f"v4l2-ctl -d {videoDev} --set-ctrl {ctrl}={value}"),stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL).returncode

def getV4L2( ctrl ) :
    ret = subprocess.run(shlex.split(f"v4l2-ctl -d {videoDev} --get-ctrl {ctrl}"),capture_output=True, text=True)
    if ret.returncode == 0 :
        return ret.stdout.split(" ")[1].strip()
    else :
        return ""

def TXTdisplay(i) :
    tempSurface = font.render(TXT[i]['text'],True,TXT[i]['color'])

    txtRect = tempSurface.get_rect()
    boxRect = txtRect.inflate(10,4)
    boxRect.topright = TXT[i]['pos']
    txtRect.center = boxRect.center

    TXT[i]['rect'] = boxRect

    txtSurface.blit(tempSurface,txtRect)
    if TXT[i]['border'] :
        pygame.draw.rect(txtSurface,TXT[i]['color'],boxRect,2)



camBrightness = int(getV4L2("brightness"))
print(f"Brightness: {camBrightness}")
image = cam.get_image()

for i in range(len(TXT)):
    TXTdisplay(i)

active = True
while active:
	events = pygame.event.get()
	for e in events:
		if (e.type == MOUSEBUTTONDOWN):
			for i in range(len(TXT)):
				if TXT[i]['rect'].collidepoint(e.pos):
					txtActive = i

			# if it didn't collide with a txt box, then it's the averaging line position
			if txtActive < 0:
				(x,y) = pygame.mouse.get_pos()

		if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
#			cam.stop()
			active = False

		if (e.type == KEYUP and e.key == K_UP):
			camBrightness = int(getV4L2("brightness"))
			camBrightness += 2
			setV4L2("brightness",camBrightness )
		if (e.type == KEYUP and e.key == K_DOWN):
			camBrightness = int(getV4L2("brightness"))
			camBrightness -= 2
			setV4L2("brightness",camBrightness )

		if (e.type == KEYUP):
			if txtActive >= 0:
				# text input
				if e.key == pygame.K_RETURN:
					txtActive = -1
				else:
					if e.key == pygame.K_BACKSPACE:
						# line is shorter, so need to clear
						pygame.draw.rect(txtSurface, BLACK, TXT[txtActive]['rect'],0)
						TXT[txtActive]['text'] = TXT[txtActive]['text'][:-1]
					else:
						TXT[txtActive]['text'] += e.unicode

					TXTdisplay(txtActive)

			else:
				if (e.key == K_SPACE):
					showAverage = not showAverage
				if (e.key == K_a):
					noAverage = not noAverage

				if (e.key == K_KP_ENTER or e.key == K_RETURN):
					timestr = time.strftime("%Y%m%d-%H%M%S")

					name = input("Name: ")
					desc = DESC['text']

					# write time averaged image (integer average, 8-bits/color)
					fileName = "./%s-spectrum-%s.jpg" % (name,timestr)
					pygame.image.save(outSurface, fileName)

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
								#iTotal += int(averageArray[xCol,yRow,zColor]) ** 2
								iTotal += int(averageArray[xCol,yRow,zColor])

						#f.write("%d,%f\n" % (xCol,math.sqrt(iTotal/(3.0*averageItems))) )
						f.write("%d,%f\n" % (xCol,iTotal/(3.0*averageItems)) )
					f.close()


	if cam.query_image():
		image = cam.get_image()

		averageIndex += 1
		averageIndex = averageIndex % averageItems

		averageArray[0:width,averageIndex] = pygame.surfarray.array3d(image)[0:width,y]

		if showAverage :
			oorSurface.fill(BLACK)	# out of range pixel errors

			# average the columns
			for xCol in range(width):
				for zColor in range(3):
					if averageArray[xCol,averageIndex,zColor] > 250:	# error, color clipped
						oorSurface.set_at((xCol,0),(255,0,0))

					iTotal = 0
					for yRow in range(averageItems):
						#iTotal += int(averageArray[xCol,yRow,zColor]) ** 2
						iTotal += int(averageArray[xCol,yRow,zColor])
					#lineSurfArray[xCol,0,zColor] = math.sqrt(iTotal/averageItems)
					lineSurfArray[xCol,0,zColor] = iTotal/averageItems

			# what does it look like without averaging?
			if noAverage:
				lineSurfArray[0:width,0] = averageArray[0:width,averageIndex]

			# convert lineSurfArray to lineSurface
			lineSurface = pygame.surfarray.make_surface(lineSurfArray)
			# fill lcd with lineSurface
			# fill it in chunks, so that you can see that something is happening...
			# ... also maybe averageItems == 50 is too much? (takes too long...)
			for i in range (int(height/8)):
				yDisplayRow += 1
				yDisplayRow = yDisplayRow % height
				outSurface.blit(lineSurface, (0,yDisplayRow))
			
			lcd.blit(outSurface,(0,0))

			# display out of range marks
			for i in range(10):
				lcd.blit(oorSurface,(0,i))	# display error bar at top of window

			# display brightness
			text = font.render(f"Brightness: {camBrightness}", True, WHITE)
			lcd.blit(text,(10,10))

			# display text
			lcd.blit(txtSurface,(0,0))

			
		else:
			lcd.blit(image, (0,0))
			pygame.draw.line(lcd, (255,0,0), (0,y), (width,y), 1)

		pygame.display.flip()

cam.stop()
