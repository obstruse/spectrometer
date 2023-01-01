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
print(f"CSVfile: {CSVfile}, CALfile: {CALfile}")

# read data file
with open(CSVfile, mode='r') as file:
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
pygame.display.set_caption('Calibrate')

pygame.init()

font = pygame.font.Font(None, 30)

WHITE = (255,255,255)
BLACK = (0,0,0)
RED   = (255,0,0)
BLUE  = (0,0,255)
GREEN = (0,255,0)
YELLOW = (0,255,255)

# surfaces
# display surface
lcd = pygame.display.set_mode(resolution)

# graph
graphSurface = pygame.surface.Surface(resolution)

# calibration
calibrateSurface = pygame.surface.Surface(resolution)

# rectangles
EUrect = pygame.Rect((resolution[0]/2,0), (resolution[0]/2,resolution[1]))
HGrect = pygame.Rect((0,0),               (resolution[0]/2,resolution[1]))

# create graph
lastPos = (0,0)
graphSurface.fill(WHITE)
for P in data[1::]:
    currentPos = (int(P[0]),resolution[1]-float(P[1]))
    if lastPos != (0,0) :
        pygame.draw.line(graphSurface,BLACK,lastPos,currentPos,2)

    lastPos = currentPos

# create calibrate
def calibrate():
    m = (Eu611 - Hg436) / (611.0 - 436.0) 
    b = 611.0 * m - Eu611

    calibrateSurface.fill(WHITE)
    calibrateSurface.set_colorkey(WHITE)

    # calibration points
    pygame.draw.line(calibrateSurface,RED,(Hg436,0),(Hg436,resolution[1]),2)
    pygame.draw.line(calibrateSurface,RED,(Eu611,0),(Eu611,resolution[1]),2)

    # cfl landmarks
    landmarks = [405, 487, 542, 546]
    for L in landmarks:
        P = L*m-b
        pygame.draw.line(calibrateSurface,BLUE,(P,0),(P,resolution[1]),1)

    # LED landmarks
    # https://gpnmag.com/article/white-leds-for-plant-applications/
    landmarks = [432,556,637]
    for L in landmarks:
        P = L*m-b
        pygame.draw.line(calibrateSurface,GREEN,(P,0),(P,resolution[1]),1)

    # CIS landmarks
    # https://photo.stackexchange.com/questions/122037/why-do-typical-imaging-sensor-colour-filter-spectral-responses-differ-so-much-fr
    landmarks = [475,510,580]
    for L in landmarks:
        P = L*m-b
        pygame.draw.line(calibrateSurface,YELLOW,(P,0),(P,resolution[1]),3)


    # camera limits
    limits = [400,700]
    for L in limits:
        P = L*m-b
        pygame.draw.line(calibrateSurface,BLACK,(P,7*resolution[1]/8),(P,resolution[1]),3)


calibrate()

lcd.blit(graphSurface,(0,0))
lcd.blit(calibrateSurface,(0,0))
pygame.display.flip()


going = True
while going:
    events = pygame.event.get()
    for e in events:
        if (e.type == MOUSEBUTTONDOWN):
            # get mouse position
            (x,y) = pygame.mouse.get_pos()
            if HGrect.collidepoint((x,y)):
                Hg436 = x
            if EUrect.collidepoint((x,y)):
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

        lcd.blit(graphSurface,(0,0))
        lcd.blit(calibrateSurface,(0,0))
        pygame.display.flip()


