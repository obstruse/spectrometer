#!/usr/bin/python3

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

"""
    read CSV file
        line zero is current calibration
    create graph layer
    create current calibration layer (transparent)
    blt graph
    blt calibration
    flip

    LOOP
        events:
            mouse button down:
                get position
                right side:
                    new col611 value
                left side:
                    new col436 value
                create current calibration layer (transparent)

            key up:
                K_KP1:
                    decrement col436 value
                K_KP3:
                    decrement col436 value
                K_KP7:
                    increment col611 value
                K_KP9:
                    increment col611 value

                create current calibration layer (transparent)

                K_s:
                    save calibration in CSV

                K_w:
                    save calibration in calibration.csv

            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                active = False

            blt graph
            blt calibration
            flip

"""
import pygame
from pygame.locals import *
#import antigravity
import time
import csv
import argparse
import pathlib

# read command line
parser = argparse.ArgumentParser(description='Calibrate')
parser.add_argument('CSVfile')

args = parser.parse_args()
CSVfile = str(pathlib.Path(args.CSVfile).with_suffix('.csv'))
CALfile = str(pathlib.Path(args.CSVfile).with_suffix('.cal'))
JPGfile = str(pathlib.Path(args.CSVfile).with_suffix('.jpg'))
BASEfile = os.path.basename(args.CSVfile)

# read data file
DATAfile = CSVfile
if os.path.exists(CALfile) :
    DATAfile = CALfile
with open(DATAfile, mode='r') as file:
    data = list(csv.reader(file))

# calibration values from CSV file
col436 = int(data[0][2])
col611 = int(data[0][3])
nm436 = 436
nm611 = 611

# width determined by length of CSV file; height is 256 for data
resolution = (len(data)-1,256)

# Calibration options
CFL = { 'type':'CFL', 'nmLeft':436, 'nmRight':611, 'mask':0b10001, 'nmLandmarks':(405, 487, 542,546)}
CIS = { 'type':'CIS', 'nmLeft':474, 'nmRight':595, 'mask':0b11110, 'nmLandmarks':(536,)}
RGB = { 'type':'RGB', 'nmLeft':436, 'nmRight':611, 'mask':0b01110, 'nmLandmarks':()}
INT = { 'type':'INT', 'nmLeft':436, 'nmRight':611, 'mask':0b00001, 'nmLandmarks':()}
CALS = ( CFL, CIS, RGB, INT )
CALindex = 0         # normally CFL options, toggle to use CIS options

(x,y) = (0,0)

# initialize display environment
pygame.display.init()
pygame.display.set_caption('Calibrate - '+BASEfile)

pygame.init()

font = pygame.font.Font(None, 30)

WHITE = (255,255,255)
BLACK = (0,0,0)
RED   = (255,0,0)
BLUE  = (128,128,255)     # lightened
GREEN = (0,255,0)
CYAN  = (0,255,255)

m = 0   # multiplier for scaling
b = 0   # offset for scaling

# surfaces
# display surface
lcd = pygame.display.set_mode(resolution)

# background
backgroundSurface = pygame.image.load(JPGfile)

# graph
graphSurface = pygame.surface.Surface(resolution)

# calibration
calibrateSurface = pygame.surface.Surface(resolution)

# rectangles
rectRight = pygame.Rect((resolution[0]/2,0), (resolution[0]/2,resolution[1]))
rectLeft  = pygame.Rect((0,0),               (resolution[0]/2,resolution[1]))

# create graph
def createGraph():
    mask = CALS[CALindex]['mask']
    type = CALS[CALindex]['type']
    pygame.display.set_caption(type+' Calibrate - '+BASEfile)

    
    graphSurface.fill(BLACK)
    graphSurface.set_colorkey(BLACK)

    if mask & 0b00001:
        lastPos = (0,0)
        for P in data[1::]:
            currentPos = (int(P[0]),resolution[1]-float(P[1]))
            if lastPos != (0,0) :
                pygame.draw.line(graphSurface,WHITE,lastPos,currentPos,2)

            lastPos = currentPos

    if mask & 0b00010:
        lastPos = (0,0)
        for P in range(resolution[0]):
            currentPos = (P, resolution[1] - backgroundSurface.get_at((P,10))[0])
            if lastPos != (0,0) :
                pygame.draw.line(graphSurface,RED,lastPos,currentPos,2)

            lastPos = currentPos

    if mask & 0b00100:
        lastPos = (0,0)
        for P in range(resolution[0]):
            currentPos = (P, resolution[1] - backgroundSurface.get_at((P,10))[1])
            if lastPos != (0,0) :
                pygame.draw.line(graphSurface,GREEN,lastPos,currentPos,2)

            lastPos = currentPos

    if mask & 0b1000:
        lastPos = (0,0)
        for P in range(resolution[0]):
            currentPos = (P, resolution[1] - backgroundSurface.get_at((P,10))[2])
            if lastPos != (0,0) :
                pygame.draw.line(graphSurface,BLUE,lastPos,currentPos,2)

            lastPos = currentPos


# draw vertical dashed line
def dashedVLine(surface, xPos, len, color=WHITE, dashLen=8, width=1) :
    yLast = 0
    yPos = 0
    while ( yPos < len):
        if yPos % (dashLen * 2) == 0 :
            yLast = yPos
        else:
            pygame.draw.line(surface,color,(xPos,yLast),(xPos,yPos),width)
        
        yPos += dashLen


# convert nm to column number
def nmCol(nm):
    return nm*m-b

# create calibrate surface
def calibrate():
    global m, b
    m = (col611 - col436) / (nm611 - nm436) 
    b = nm611 * m - col611

    calibrateSurface.fill(BLACK)
    calibrateSurface.set_colorkey(BLACK)

    nmLeft      = CALS[CALindex]['nmLeft']
    nmRight     = CALS[CALindex]['nmRight']
    nmLandmarks = CALS[CALindex]['nmLandmarks']

    # calibration points
    if CALS[CALindex]['mask'] & 0b10000 :
        dashedVLine(calibrateSurface,nmCol(nmLeft) ,resolution[1],WHITE,12,3)
        dashedVLine(calibrateSurface,nmCol(nmRight),resolution[1],WHITE,12,3)
        # camera limits
        nmLimits = [400,700]
        for L in nmLimits:
            P = nmCol(L)
            pygame.draw.line(calibrateSurface,RED,(P,7*resolution[1]/8),(P,resolution[1]),3)

            
    # landmarks
    for L in nmLandmarks:
        dashedVLine(calibrateSurface,nmCol(L),resolution[1],WHITE,4,1)

    ## LED landmarks
    ## https://gpnmag.com/article/white-leds-for-plant-applications/
    #landmarks = [432,556,637]


createGraph()
calibrate()

lcd.blit(backgroundSurface,(0,0))
lcd.blit(graphSurface,(0,0))
lcd.blit(calibrateSurface,(0,0))
pygame.display.flip()


# throttle
timer = pygame.time.Clock()

active = True
while active:
    timer.tick(10)

    events = pygame.event.get()
    for e in events:
        if (e.type == MOUSEBUTTONDOWN):
            # get mouse position
            (x,y) = pygame.mouse.get_pos()
            if rectLeft.collidepoint((x,y)):
                nmLeft = CALS[CALindex]['nmLeft']
                m = (col611 - x) / (nm611 - nmLeft) 
                b = nmLeft * m - x
                col436 = nmCol(nm436)
            
            if rectRight.collidepoint((x,y)):
                nmRight = CALS[CALindex]['nmRight'] 
                m = (x - col436) / (nmRight - nm436) 
                b = nmRight * m - x
                col611 = nmCol(nm611)
            
            calibrate()

        if e.type == KEYUP :
            if e.key == K_KP1:
                col436 -= 1
            if e.key == K_KP3:
                col436 += 1

            if e.key == K_KP7:
                col611 -= 1
            if e.key == K_KP9:
                col611 += 1

            if e.key == K_c:
                CALindex += 1
                CALindex = CALindex % len(CALS)
                createGraph()

            calibrate()

            if e.key == K_s:        # save calibration in .CAL file
                with open(CALfile,'w') as CAL:
                    data[0][2] = col436
                    data[0][3] = col611
                    C = csv.writer(CAL)
                    C.writerows(data)

            #if e.key == K_w:        # save calibration in calibration.csv
            # 

        if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
            active = False

        lcd.blit(backgroundSurface,(0,0))
        lcd.blit(graphSurface,(0,0))
        lcd.blit(calibrateSurface,(0,0))
        pygame.display.flip()


