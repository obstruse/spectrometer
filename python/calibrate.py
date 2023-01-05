#!/usr/bin/python3

import os
#os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

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
                    new EU611 value
                left side:
                    new Hg436 value
                create current calibration layer (transparent)

            key up:
                K_KP1:
                    decrement Hg436 value
                K_KP7:
                    increment Hg436 value
                K_KP3:
                    decrement Eu611 value
                K_KP9:
                    increment Hg436 value

                create current calibration layer (transparent)

                K_s:
                    save calibration in CSV

                K_w:
                    save calibration in calibration.csv

            if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                going = False

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
CSVfile = pathlib.Path(args.CSVfile).with_suffix('.csv')
CALfile = pathlib.Path(args.CSVfile).with_suffix('.cal')
JPGfile = pathlib.Path(args.CSVfile).with_suffix('.jpg')
BASEfile = os.path.basename(args.CSVfile)
print(f"CSVfile: {CSVfile}, CALfile: {CALfile}")

# read data file
DATAfile = CSVfile
if os.path.exists(CALfile) :
    DATAfile = CALfile
with open(DATAfile, mode='r') as file:
    data = list(csv.reader(file))

# calibration values from CSV file
Hg436 = int(data[0][2])
Eu611 = int(data[0][3])
print(f"Hg436: {Hg436}, Eu611: {Eu611}")

# width determined by length of CSV file; height is 256 for data
resolution = (len(data)-1,256)
(x,y) = (0,0)

# initialize display environment
pygame.display.init()
pygame.display.set_caption('Calibrate - '+BASEfile)

pygame.init()

font = pygame.font.Font(None, 30)

WHITE = (255,255,255)
BLACK = (0,0,0)
RED   = (255,0,0)
BLUE  = (0,0,255)
GREEN = (0,255,0)
CYAN = (0,255,255)

use_CIS = False         # normally CFL landmarks, toggle to use CIS landmarks

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
EUrect = pygame.Rect((resolution[0]/2,0), (resolution[0]/2,resolution[1]))
HGrect = pygame.Rect((0,0),               (resolution[0]/2,resolution[1]))

# create graph
def createGraph():
    lastPos = (0,0)
    graphSurface.fill(BLACK)
    graphSurface.set_colorkey(BLACK)
    if use_CIS:
        print("graph cis")
        for P in range(resolution[0]):
            currentPos = (P, resolution[1] - backgroundSurface.get_at((P,10))[0])
            if lastPos != (0,0) :
                pygame.draw.line(graphSurface,RED,lastPos,currentPos,2)

            lastPos = currentPos

        lastPos = (0,0)
        for P in range(resolution[0]):
            currentPos = (P, resolution[1] - backgroundSurface.get_at((P,10))[1])
            if lastPos != (0,0) :
                pygame.draw.line(graphSurface,GREEN,lastPos,currentPos,2)

            lastPos = currentPos

        lastPos = (0,0)
        for P in range(resolution[0]):
            currentPos = (P, resolution[1] - backgroundSurface.get_at((P,10))[2])
            if lastPos != (0,0) :
                pygame.draw.line(graphSurface,BLUE,lastPos,currentPos,2)

            lastPos = currentPos

    else:
        for P in data[1::]:
            currentPos = (int(P[0]),resolution[1]-float(P[1]))
            if lastPos != (0,0) :
                pygame.draw.line(graphSurface,WHITE,lastPos,currentPos,2)

            lastPos = currentPos

# draw dashed line
def dashedVLine(surface, xPos, len, color=WHITE, dashLen=8, width=1) :
    yLast = 0
    yPos = 0
    while ( yPos < len):
        if yPos % (dashLen * 2) == 0 :
            yLast = yPos
        else:
            pygame.draw.line(surface,color,(xPos,yLast),(xPos,yPos),width)
        
        yPos += dashLen


# create calibrate
def calibrate():
    m = (Eu611 - Hg436) / (611.0 - 436.0) 
    b = 611.0 * m - Eu611

    calibrateSurface.fill(BLACK)
    calibrateSurface.set_colorkey(BLACK)

    # calibration points
    #pygame.draw.line(calibrateSurface,RED,(Hg436,0),(Hg436,resolution[1]),2)
    #pygame.draw.line(calibrateSurface,RED,(Eu611,0),(Eu611,resolution[1]),2)

    if use_CIS :
        # calibration points
        dashedVLine(calibrateSurface,474*m-b,resolution[1],WHITE,12,3)
        dashedVLine(calibrateSurface,595*m-b,resolution[1],WHITE,12,3)
        
        # CIS landmarks
        # https://photo.stackexchange.com/questions/122037/why-do-typical-imaging-sensor-colour-filter-spectral-responses-differ-so-much-fr
        #landmarks = [475,510,580]
        landmarks = [474,536,595]
        for L in landmarks:
            P = L*m-b
            #pygame.draw.line(calibrateSurface,CYAN,(P,0),(P,resolution[1]),3)
            dashedVLine(calibrateSurface,P,resolution[1],WHITE,4,1)
    else:
        # calibration points
        dashedVLine(calibrateSurface,Hg436,resolution[1],WHITE,12,3)
        dashedVLine(calibrateSurface,Eu611,resolution[1],WHITE,12,3)
        # cfl landmarks
        landmarks = [405, 487, 542, 546]
        for L in landmarks:
            P = L*m-b
            #pygame.draw.line(calibrateSurface,BLUE,(P,0),(P,resolution[1]),1)
            dashedVLine(calibrateSurface,P,resolution[1],WHITE,4,1)

    ## LED landmarks
    ## https://gpnmag.com/article/white-leds-for-plant-applications/
    #landmarks = [432,556,637]
    #for L in landmarks:
    #    P = L*m-b
    #    pygame.draw.line(calibrateSurface,GREEN,(P,0),(P,resolution[1]),1)

    ## CIS landmarks
    ## https://photo.stackexchange.com/questions/122037/why-do-typical-imaging-sensor-colour-filter-spectral-responses-differ-so-much-fr
    #landmarks = [475,510,580]
    #for L in landmarks:
    #    P = L*m-b
    #    pygame.draw.line(calibrateSurface,CYAN,(P,0),(P,resolution[1]),3)


    # camera limits
    limits = [400,700]
    for L in limits:
        P = L*m-b
        pygame.draw.line(calibrateSurface,RED,(P,7*resolution[1]/8),(P,resolution[1]),3)

def nmCol(nm):
    return nm*m-b

createGraph()
calibrate()

lcd.blit(backgroundSurface,(0,0))
lcd.blit(graphSurface,(0,0))
lcd.blit(calibrateSurface,(0,0))
pygame.display.flip()


# throttle
timer = pygame.time.Clock()

going = True
while going:
    timer.tick(10)

    events = pygame.event.get()
    for e in events:
        if (e.type == MOUSEBUTTONDOWN):
            # get mouse position
            (x,y) = pygame.mouse.get_pos()
            if HGrect.collidepoint((x,y)):
                if use_CIS:
                    m = (Eu611 - x) / (611.0 - 475.0) 
                    b = 611.0 * m - Eu611
                    Hg436 = nmCol(436)
                else:
                    Hg436 = x
            
            if EUrect.collidepoint((x,y)):
                if use_CIS:   
                    m = (x - Hg436) / (580.0 - 436.0) 
                    b = 580.0 * m - x
                    Eu611 = nmCol(611)
                else:
                    Eu611 = x

            calibrate()

        if e.type == KEYUP :
            if e.key == K_KP1:
                Hg436 -= 1
            if e.key == K_KP3:
                Hg436 += 1

            if e.key == K_KP7:
                Eu611 -= 1
            if e.key == K_KP9:
                Eu611 += 1

            if e.key == K_c:
                use_CIS = not use_CIS
                createGraph()

            calibrate()

            if e.key == K_s:        # save calibration in .CAL file
                with open(CALfile,'w') as CAL:
                    data[0][2] = Hg436
                    data[0][3] = Eu611
                    C = csv.writer(CAL)
                    C.writerows(data)

            #if e.key == K_w:        # save calibration in calibration.csv
            # 

        if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
            going = False

        lcd.blit(backgroundSurface,(0,0))
        lcd.blit(graphSurface,(0,0))
        lcd.blit(calibrateSurface,(0,0))
        pygame.display.flip()


