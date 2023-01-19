#!/usr/bin/python3

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

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
# 'with_suffix' will replace a trailing dot-suffix, but will append to a trailing dot:
CSVfile = str(pathlib.Path(args.CSVfile.rstrip('.')).with_suffix('.csv'))
CALfile = str(pathlib.Path(args.CSVfile.rstrip('.')).with_suffix('.cal'))
JPGfile = str(pathlib.Path(args.CSVfile.rstrip('.')).with_suffix('.jpg'))
BASEfile, ext = os.path.splitext(os.path.basename(args.CSVfile.rstrip('.')))

# read CSV file
DATAfile = CSVfile
if os.path.exists(CALfile) :
    DATAfile = CALfile
with open(DATAfile, mode='r') as file:
    data = list(csv.reader(file))

# calibration values from CSV file.  They may be present, or null...
calibrateMultiplier = float(data[0][0] or 0)
calibrateOffset     = float(data[0][1] or 0)
# for compatibility with old data files. Not used:
#col436 = int(data[0][2] or 0)
#col611 = int(data[0][3] or 0)
#nm436 = 436
#nm611 = 611

# initialize display environment
pygame.display.init()
pygame.init()

font = pygame.font.Font(None, 24)

WHITE = (255,255,255)
BLACK = (0,0,0)
RED   = (255,0,0)
BLUE  = (128,128,255)     # lightened
GREEN = (0,255,0)
CYAN  = (0,255,255)

# width determined by length of CSV file; height is 256 for data
width = len(data)-1     # minus the header line
height = 256
resolution = (width,height)
(x,y) = (0,0)

# Calibration Dictionary
C = {"CFL":{'nmLeft':436, 'nmRight':611, 'mask':0b10001, 'nmLandmarks':(405, 487, 542,546)},
        "CIS":{'nmLeft':465, 'nmRight':596, 'mask':0b11110, 'nmLandmarks':(529,532)},
        "RGB":{'nmLeft':436, 'nmRight':611, 'mask':0b01110, 'nmLandmarks':()},
        "INT":{'nmLeft':436, 'nmRight':611, 'mask':0b00001, 'nmLandmarks':()}
}
CALindex = "CFL"

# Button Dictionary
bottomRow = height-10
B = { "CFL":{"pos":(10,bottomRow), "text":"CFL", "align":"BL", "cal":"CFL" },
      "CIS":{"rightof":"CFL", "text":"CIS", "cal":"CIS"},
      #"RGB":{"rightof":"CIS", "text":"RGB", "cal":"RGB"},
      #"INT":{"rightof":"RGB", "text":"INT", "cal":"INT"},
	  "QUIT":{"pos":(width-10,bottomRow),   "text":"QUIT", "align":"BR", "bg":RED},
      "SAVE":{"pos":(width/2,bottomRow),    "text":"SAVE",  "align":"MB", "bg":GREEN, "color":(1,1,1) }
}

# surfaces
# display surface
lcd = pygame.display.set_mode(resolution)

# background
backgroundSurface = pygame.image.load(JPGfile)

# graph (CFL or CIS graphs)
graphSurface = pygame.surface.Surface(resolution)

# calibration (calibration points and landmarks)
calibrateSurface = pygame.surface.Surface(resolution)

# rectangles
rectRight = pygame.Rect((resolution[0]/2,0), (resolution[0]/2,resolution[1]))
rectLeft  = pygame.Rect((0,0),               (resolution[0]/2,resolution[1]))

# text surface (where the buttons go)
txtSurface = pygame.surface.Surface(resolution)
txtSurface.fill(BLACK)
txtSurface.set_colorkey(BLACK)

# utility functions

# convert nm to column number
def nmCol(nm):
    return nm * calibrateMultiplier - calibrateOffset

# create a graph.  The lines included specified by mask. might be average, or red, green, blue
def createGraph():
    mask = C[CALindex]['mask']
    pygame.display.set_caption(' Calibrate - '+BASEfile)
    
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


# calculate calibrate multiplier and offset, and create calibrate surface
def calibrate(nmLeft=0, nmRight=0, colLeft=0, colRight=0):
    global calibrateMultiplier, calibrateOffset

    if nmLeft != 0 :
        # parameters are given, calculate multiplier and offset
        calibrateMultiplier = (colRight - colLeft) / (nmRight - nmLeft) 
        calibrateOffset     = nmLeft * calibrateMultiplier - colLeft
    if calibrateMultiplier == 0 :
        # set default values
        calibrateMultiplier = (width - 0) / (700 - 400)
        calibrateOffset     = 400 * calibrateMultiplier - 0

    calibrateSurface.fill(BLACK)
    calibrateSurface.set_colorkey(BLACK)

    nmLeft      = C[CALindex]['nmLeft']
    nmRight     = C[CALindex]['nmRight']
    nmLandmarks = C[CALindex]['nmLandmarks']

    # calibration points
    if C[CALindex]['mask'] & 0b10000 :
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

# display item from button dictionary (B)
def TXTdisplay(key) :

    # position to the right of a previous entry in the dictionary
    rightof = B[key].get('rightof',"") 
    if rightof != "" :
        B[key]['pos'] = B[rightof]['rect'].bottomright
        B[key]['align'] = 'BL'

    tempSurface = font.render(B[key].get('text',""),True,B[key].get('color',WHITE))

	# the line might be shorter, clear the previous box
    pygame.draw.rect(txtSurface, BLACK, B[key].get('rect',(0,0,0,0)),0)

    txtRect = tempSurface.get_rect()
    boxRect = txtRect.inflate(10,4)     # give the box some air...
    align = B[key].get('align','BR')
    if align == 'BR' :
        boxRect.bottomright = B[key]['pos']
    if align == 'BL':
        boxRect.bottomleft = B[key]['pos']
    if align == 'MB' :
        boxRect.midbottom = B[key]['pos']

    #print(f"name: {B[key]['name']}, size: {boxRect.size}")
    txtRect.center = boxRect.center     # put the text in the center of the box

    B[key]['rect'] = boxRect

    pygame.draw.rect(txtSurface,B[key].get('bg',(1,1,1)),boxRect,0)	# text background default to almost black. can't use black: it's transparent
    txtSurface.blit(tempSurface,txtRect)
    if B[key].get('border',True) :
        pygame.draw.rect(txtSurface,WHITE,boxRect,2)

def TXThighlight(key,highlight) :
    if key in B :
        if highlight :
            pygame.draw.rect(txtSurface,RED,B[key]['rect'],2)
        else:
            pygame.draw.rect(txtSurface,WHITE,B[key]['rect'],2)


# create the text surface
for key in list(B):
    TXTdisplay(key)
# highlight the current calibration index
TXThighlight(CALindex,True)

createGraph()
calibrate()

lcd.blit(backgroundSurface,(0,0))
lcd.blit(graphSurface,(0,0))
lcd.blit(calibrateSurface,(0,0))
lcd.blit(txtSurface,(0,0))
pygame.display.flip()


# throttle
timer = pygame.time.Clock()

active = True
while active:
    timer.tick(10)

    events = pygame.event.get()
    for e in events:
        if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
            active = False

        if (e.type == MOUSEBUTTONDOWN):
            txtActive = ""			# a click anywhere ends any active txt inputs
            for key in list(B):
                # collide with dictionary
                if B[key]['rect'].collidepoint(e.pos):
                    B[key]['value'] = 1
                    txtActive = key
                    if 'cal' in B[key] :
                        # if the key has a 'cal' entry, switch to it and update graph/calibrate
                        TXThighlight(CALindex,False)
                        CALindex = B[key]['cal']
                        TXThighlight(CALindex,True)
                        createGraph()
                        calibrate()
                    break
            
            if txtActive == "" :
                # didn't collide with any dictionary item
                # ...so it's a calibration point
                (x,y) = pygame.mouse.get_pos()
                nmLeft = C[CALindex]['nmLeft']
                nmRight = C[CALindex]['nmRight'] 
                colLeft = nmCol(nmLeft)
                colRight = nmCol(nmRight)
                if rectLeft.collidepoint((x,y)):
                    colLeft = x
                
                if rectRight.collidepoint((x,y)):
                    colRight = x
                
                calibrate(nmLeft, nmRight, colLeft, colRight)

        if e.type == KEYDOWN :
            nmLeft = C[CALindex]['nmLeft']
            nmRight = C[CALindex]['nmRight'] 
            colLeft = nmCol(nmLeft)
            colRight = nmCol(nmRight)
            if e.key == K_KP1 or e.key == K_z:
                colLeft -= 1
            if e.key == K_KP3 or e.key == K_c:
                colLeft += 1

            if e.key == K_KP7 or e.key == K_q:
                colRight -= 1
            if e.key == K_KP9 or e.key == K_e:
                colRight += 1

            calibrate(nmLeft, nmRight, colLeft, colRight)


        lcd.blit(backgroundSurface,(0,0))
        lcd.blit(graphSurface,(0,0))
        lcd.blit(calibrateSurface,(0,0))
        lcd.blit(txtSurface,(0,0))
        pygame.display.flip()

    # after every frame, check actions
    if B['QUIT'].get('value',0) > 0:
        active = False

    if B['SAVE'].get('value',0) > 0:
        B['SAVE']['value'] = 0    
        with open(CALfile,'w') as CAL:
            data[0][0] = calibrateMultiplier
            data[0][1] = calibrateOffset
            data[0][2] = int(nmCol(436))     # old version
            data[0][3] = int(nmCol(611))     # old version
            C = csv.writer(CAL)
            C.writerow(data[0])

            if len(data[1]) == 5 :
                # copy data to CAL file
                C.writerows(data[1:])
            else:
                # old version of spectralAverage didn't write the averaged RGB values
                # ... so this creates the missing values from the JPG file for compatibility
                for i in range(1, len(data)) :
                    C.writerow([data[i][0],data[i][1],backgroundSurface.get_at((i-1,10))[0],backgroundSurface.get_at((i-1,10))[1],backgroundSurface.get_at((i-1,10))[2]])


