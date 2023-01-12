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
pixelClip = config.getint('Spectrometer','pixelClip',fallback=250)
calibDefault = config.get('Spectrometer','calibDefault',fallback=',,410,900')

# read command line, to override the config file settings
parser = argparse.ArgumentParser(description='Spectrometer')
parser.add_argument('-x','--width'     ,dest='width',default=width,type=int)
parser.add_argument('-y','--height'    ,dest='height',default=height,type=int)
parser.add_argument('-v','--video'     ,dest='videoDev',default=videoDev)
parser.add_argument('-a','--average'   ,dest='averageItems',default=averageItems,type=int)
parser.add_argument('-c','--clip'      ,dest='pixelClip',default=pixelClip,type=int)

args = parser.parse_args()
width = args.width
height = args.height
videoDev = args.videoDev
averageItems = args.averageItems
pixelClip = args.pixelClip

pygame.init()
pygame.camera.init()

fontSize = 24
font = pygame.font.Font(None, fontSize)

WHITE = (255,255,255)
BLACK = (0,0,0)
RED   = (255,0,0)
BLUE  = (0,0,255)
GREEN = (0,255,0)
CYAN  = (0,255,255)

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
	calibration = calibDefault

lcd = pygame.display.set_mode(resolution)

cam = pygame.camera.Camera(videoDev,resolution)
cam.start()

D = { "DESC":{"name":"description", "pos":(width/2+30,height-fontSize-10), "text":"description", "align":"TL"},
      "TAG":{"name":"tag",          "pos":(width/2-30,height-fontSize-10), "text":"prefix",      "align":"TR" },
	  "BRIGHT":{"name":"brightness","pos":(10,height-fontSize-10),         "text":"",           "align":"TL", "border":False, "bg":BLACK },
	  "QUIT":{"name":"quit",        "pos":(width-10,height-fontSize-10),   "text":"QUIT", "align":"TR", "bg":RED},
      "SAVE":{"name":"save",        "pos":(width/2,height-fontSize-10),    "text":"SAVE",  "align":"MT", "bg":GREEN, "color":(1,1,1) },
      "AVERAGE":{"name":"average",  "pos":(width/4,height-fontSize-10),    "text":"AVERAGE", "align":"MT", "bg":BLUE}
}

txtActive = ""		# a text object is active and wants attention. the value is the dictionary key to the object.

#utility functions
def setV4L2( ctrl, value ) :
    return subprocess.run(shlex.split(f"v4l2-ctl -d {videoDev} --set-ctrl {ctrl}={value}"),stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL).returncode

def getV4L2( ctrl ) :
    ret = subprocess.run(shlex.split(f"v4l2-ctl -d {videoDev} --get-ctrl {ctrl}"),capture_output=True, text=True)
    if ret.returncode == 0 :
        return ret.stdout.split(" ")[1].strip()
    else :
        return ""

def TXTdisplay(key) :
	tempSurface = font.render(D[key].get('text',""),True,D[key].get('color',WHITE))

	# if the line is shorter, need to clear previous box
	pygame.draw.rect(txtSurface, BLACK, D[key].get('rect',(0,0,0,0)),0)

	txtRect = tempSurface.get_rect()
	boxRect = txtRect.inflate(10,4)
	align = D[key].get('align','TR')
	if align == 'TR' :
		boxRect.topright = D[key]['pos']
	if align == 'TL':
		boxRect.topleft = D[key]['pos']
	if align == 'MT' :
		boxRect.midtop = D[key]['pos']

	#print(f"name: {D[key]['name']}, size: {boxRect.size}")
	txtRect.center = boxRect.center

	D[key]['rect'] = boxRect

	pygame.draw.rect(txtSurface,D[key].get('bg',(1,1,1)),boxRect,0)	# text background default to almost black. can't use black: it's transparent
	txtSurface.blit(tempSurface,txtRect)
	if D[key].get('border',True) :
		pygame.draw.rect(txtSurface,WHITE,boxRect,2)



camBrightness = int(getV4L2("brightness"))
D['BRIGHT']['text'] = f"Brightness: {camBrightness}"

# display all of the objects
for key in list(D):
    TXTdisplay(key)

image = cam.get_image()

active = True
while active:
	events = pygame.event.get()
	for e in events:
		if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
			active = False

		if (e.type == MOUSEBUTTONDOWN):
			txtActive = ""			# a click anywhere ends any active txt inputs
			for key in list(D):
    			# collide with dictionary
				if D[key]['rect'].collidepoint(e.pos):
					D[key]['value'] = 1
					txtActive = key
					break
			
			if txtActive == "" :
				# so, didn't collide with anything
				if showAverage :	# if showing average, mouse click is only for box collisions
					continue
				else:				# ... otherwise mouse click is also selects the averaging line
					(x,y) = e.pos

		if (e.type == KEYUP and e.key == K_UP):
			camBrightness = int(getV4L2("brightness"))
			camBrightness += 2
			setV4L2("brightness",camBrightness )
			D['BRIGHT']['text'] = f"Brightness: {camBrightness}"
			TXTdisplay('BRIGHT')
		if (e.type == KEYUP and e.key == K_DOWN):
			camBrightness = int(getV4L2("brightness"))
			camBrightness -= 2
			setV4L2("brightness",camBrightness )
			D['BRIGHT']['text'] = f"Brightness: {camBrightness}"
			TXTdisplay('BRIGHT')

		if (e.type == KEYUP):
			if txtActive != "":
				# text input
				if e.key == pygame.K_RETURN:
					txtActive = ""
				else:
					if e.key == pygame.K_BACKSPACE:
						D[txtActive]['text'] = D[txtActive]['text'][:-1]
					else:
						D[txtActive]['text'] += e.unicode

					TXTdisplay(txtActive)

			else:
				if (e.key == K_a):
					noAverage = not noAverage

	# camera stuff
	if cam.query_image():
		image = cam.get_image()

		averageIndex += 1
		averageIndex = averageIndex % averageItems

		averageArray[0:width,averageIndex] = pygame.surfarray.array3d(image)[0:width,y]

		if showAverage :
    		# average line over time
			oorSurface.fill(BLACK)	# initialize out of range pixel errors

			# average the columns
			for xCol in range(width):
				for zColor in range(3):
					if averageArray[xCol,averageIndex,zColor] > pixelClip:	# value (almost) clipped
						oorSurface.set_at((xCol,0),(255,0,0))

					iTotal = 0
					for yRow in range(averageItems):
						iTotal += averageArray[xCol,yRow,zColor]
					lineSurfArray[xCol,0,zColor] = int(iTotal/averageItems)

			## what does it look like without averaging?
			if noAverage:
				lineSurfArray[0:width,0] = averageArray[0:width,averageIndex]

			# convert lineSurfArray to lineSurface
			lineSurface = pygame.surfarray.make_surface(lineSurfArray)
			# fill lcd with lineSurface
			# fill it in chunks, so that you can see that something is happening...
			for i in range (int(height/8)):
				yDisplayRow += 1
				yDisplayRow = yDisplayRow % height
				outSurface.blit(lineSurface, (0,yDisplayRow))
			
			# the average surface...
			lcd.blit(outSurface,(0,0))

			# ...and Out Of Range marks
			for i in range(10):
				lcd.blit(oorSurface,(0,i))	# display OOR at top of window
			
		else:
    		# camera image with averaging line
			lcd.blit(image, (0,0))
			pygame.draw.line(lcd, (255,0,0), (0,y), (width,y), 1)

		# display text layer over everything
		lcd.blit(txtSurface,(0,0))

		pygame.display.flip()


	# after every frame, check actions
	if D['QUIT'].get('value',0) > 0:
		active = False

	if D['AVERAGE'].get('value',0) > 0:
		showAverage = not showAverage
		D['AVERAGE']['value'] = 0
		txtActive = ""
    
	if D['SAVE'].get('value',0) > 0:
		D['SAVE']['value'] = 0
		txtActive = ""

		timestr = time.strftime("%Y%m%d-%H%M%S")

		name = D['TAG'].get('text','UNK')
		desc = D['DESC'].get('text','unknown')

		# write time averaged image (integer average, 8-bits/color)
		fileName = "./%s-%s.jpg" % (name,timestr)
		pygame.image.save(outSurface, fileName)
		# a little bit of feedback for the operation
		pygame.display.set_caption(fileName)

		# write time averaged CSV, floating-point averaged colors
		fileName = "./%s-%s.csv" % (name,timestr)
		f = open(fileName, "x")
		f.write( "%s,%s,%s\n" % (calibration.strip(),name,desc) )

		# each column
		for xCol in range (width):
			z0 = 0
			z1 = 0
			z2 = 0
			# average over time
			for yRow in range(averageItems):
				# average the colors
				z0 += averageArray[xCol,yRow,0]
				z1 += averageArray[xCol,yRow,1]
				z2 += averageArray[xCol,yRow,2]
				#for zColor in range(3):
				#	iTotal += averageArray[xCol,yRow,zColor]
			
			iTotal = (z0 + z1 + z2)/3.0/averageItems
			z0 = z0/averageItems
			z1 = z1/averageItems
			z2 = z2/averageItems
			f.write("%d,%f,%f,%f,%f\n" % (xCol,iTotal,z0,z1,z2) )
		f.close()

cam.stop()
