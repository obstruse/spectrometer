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
width = len(data)-1
height = 256
resolution = (width,height)
(x,y) = (0,0)

m = 0   # multiplier for scaling
b = 0   # offset for scaling

# Calibration options
CALS = {"CFL":{'nmLeft':436, 'nmRight':611, 'mask':0b10001, 'nmLandmarks':(405, 487, 542,546)},
        "CIS":{'nmLeft':474, 'nmRight':595, 'mask':0b11110, 'nmLandmarks':(536,)},
        "RGB":{'nmLeft':436, 'nmRight':611, 'mask':0b01110, 'nmLandmarks':()},
        "INT":{'nmLeft':436, 'nmRight':611, 'mask':0b00001, 'nmLandmarks':()}
}
CALindex = "CFL"

# buttons
bottomRow = height-10
D = { "CFL":{"pos":(10,bottomRow), "text":"CFL", "align":"BL", "cal":"CFL" },
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

# graph
graphSurface = pygame.surface.Surface(resolution)

# calibration
calibrateSurface = pygame.surface.Surface(resolution)

# rectangles
rectRight = pygame.Rect((resolution[0]/2,0), (resolution[0]/2,resolution[1]))
rectLeft  = pygame.Rect((0,0),               (resolution[0]/2,resolution[1]))

# text surface
txtSurface = pygame.surface.Surface(resolution)
txtSurface.fill(BLACK)
txtSurface.set_colorkey(BLACK)

# utility functions
def createGraph():
    mask = CALS[CALindex]['mask']
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


def TXTdisplay(key) :
    # position to the right of a previous entry in the dictionary
    rightof = D[key].get('rightof',"") 
    if rightof != "" :
        D[key]['pos'] = D[rightof]['rect'].bottomright
        D[key]['align'] = 'BL'

    tempSurface = font.render(D[key].get('text',""),True,D[key].get('color',WHITE))

	# if the line is shorter, need to clear previous box
    pygame.draw.rect(txtSurface, BLACK, D[key].get('rect',(0,0,0,0)),0)

    txtRect = tempSurface.get_rect()
    boxRect = txtRect.inflate(10,4)
    align = D[key].get('align','BR')
    if align == 'BR' :
        boxRect.bottomright = D[key]['pos']
    if align == 'BL':
        boxRect.bottomleft = D[key]['pos']
    if align == 'MB' :
        boxRect.midbottom = D[key]['pos']

    #print(f"name: {D[key]['name']}, size: {boxRect.size}")
    txtRect.center = boxRect.center

    D[key]['rect'] = boxRect

    pygame.draw.rect(txtSurface,D[key].get('bg',(1,1,1)),boxRect,0)	# text background default to almost black. can't use black: it's transparent
    txtSurface.blit(tempSurface,txtRect)
    if D[key].get('border',True) :
        pygame.draw.rect(txtSurface,WHITE,boxRect,2)

def TXThighlight(key,highlight) :
    if key in D :
        if highlight :
            pygame.draw.rect(txtSurface,RED,D[key]['rect'],2)
        else:
            pygame.draw.rect(txtSurface,WHITE,D[key]['rect'],2)


# create the text surface
for key in list(D):
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
            for key in list(D):
                # collide with dictionary
                if D[key]['rect'].collidepoint(e.pos):
                    D[key]['value'] = 1
                    txtActive = key
                    if 'cal' in D[key] :
                        # if the key has a 'cal' entry, switch to it and update graph/calibrate
                        TXThighlight(CALindex,False)
                        CALindex = D[key]['cal']
                        TXThighlight(CALindex,True)
                        createGraph()
                        calibrate()
                    break
            
            if txtActive == "" :
                # didn't collide with any dictionary item
                # ...so it's a calibration point
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

        if e.type == KEYDOWN :
            if e.key == K_KP1 or e.key == K_z:
                col436 -= 1
            if e.key == K_KP3 or e.key == K_c:
                col436 += 1

            if e.key == K_KP7 or e.key == K_q:
                col611 -= 1
            if e.key == K_KP9 or e.key == K_e:
                col611 += 1

            calibrate()


        lcd.blit(backgroundSurface,(0,0))
        lcd.blit(graphSurface,(0,0))
        lcd.blit(calibrateSurface,(0,0))
        lcd.blit(txtSurface,(0,0))
        pygame.display.flip()

    # after every frame, check actions
    if D['QUIT'].get('value',0) > 0:
        active = False

    if D['SAVE'].get('value',0) > 0:
        D['SAVE']['value'] = 0    
        with open(CALfile,'w') as CAL:
            data[0][2] = int(col436)
            data[0][3] = int(col611)
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


