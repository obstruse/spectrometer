#!/bin/bash

BASE="$1"
CSV="${BASE%.*}.csv"
JPG="${BASE%.*}.jpg"

C436=$(awk -F ',' '{print $3;exit}' $CSV)
C611=$(awk -F ',' '{print $4;exit}' $CSV)
SNAME=$(awk -F ',' '{print $5;exit}' $CSV)
SDESC=$(awk -F ',' '{print $6;exit}' $CSV)

export NO_AT_BRIDGE=1

gnuplot <<EOF

set term qt size 1280,720
#set terminal pngcairo enhanced size 1280,720 
#set output 'intensity2.png'

set datafile separator ","

##set label "$SDESC" at graph 0,character 3  tc "white" front
##set label "nm" at graph 0.98,character 1 tc "white" front

set yrange [0:719]
set y2range [-12:255]
unset ytics

m = (611.0 - 436.0) / ($C611 - $C436)   # calibration multiplier
b = 611.0 - m * $C611                   # calibration offset

set style line 1 lw 1 lc rgb "white"
set style arrow 1 nohead front lc rgb "white" dashtype 2

set xrange [0:1279]
#set grid xtics lc rgb "white" front # use set grid to get xtic marks white and in front
unset grid                          # ...unset grid to turn off the grid lines
#set xtics axis in 50 tc "white"     # put the tics on the zero axis and tic text white
#set border ls 1                     # tic lines use the border color
#set xtics nomirror
#set mxtics  5
#set xzeroaxis ls 1                 # draw zero line (or not. Changes label position)
unset key

set autoscale noextend
set border 0
set lmargin screen 0
set bmargin screen 0
set rmargin screen 1
set tmargin screen 1

#set arrow from 405,graph 0 to 405,720 as 1
#set label "Hg405" at 405,character 3 tc "white" front
#set arrow from 436,graph 0 to 436,720 as 1
#set label "Hg436" at 436,character 3 tc "white" front
#set arrow from 487,graph 0 to 487,720 as 1
#set label "Tb487" at 487,character 3 tc "white" front
#set arrow from 542,graph 0 to 542,720 as 1
#set arrow from 546,graph 0 to 546,720 as 1
#set label "Hg546" at 546,character 3 tc "white" front
#set arrow from 611,graph 0 to 611,720 as 1
#set label "Eu611" at 611,character 3 tc "white" front

plot "$JPG" binary filetype=jpg with rgbimage axes x1y1, \
     "$CSV" using 1:2:(-12) skip 1  notitle lc rgb "black" with filledcurves fs transparent solid 1.0 axes x1y2,  \
     "$CSV" using 1:2       skip 1 ls 1 notitle with lines axes x1y2

pause mouse button2 "button2 to exit"

EOF
