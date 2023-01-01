set datafile separator ","
set ylabel 'Intensity'
#set ytics nomirror
set grid ytics lw 2
set xlabel 'nm'

#if (!exists("spectrum")) spectrum='spectrum-20181208-101610.csv'
c436 = system("awk -F ',' '{print $3;exit}' ".spectrum)
c611 = system("awk -F ',' '{print $4;exit}' ".spectrum)
sname = system("awk -F ',' '{print $5;exit}' ".spectrum)
print sname
sdesc = system("awk -F ',' '{print $6;exit}' ".spectrum)
print sdesc
snameTitle = sname
sdescTitle = sdesc
set label sdesc at graph 0,0.05

m = (611.0 - 436.0) / (c611 - c436)
b = 611.0 - m * c611
print m
print b

set xrange [b+1:]
set yrange [0:]

set arrow from 405,0 to 405,255 nohead dashtype 3
set label "Hg405" at 405,5
set arrow from 436,0 to 436,255 nohead dashtype 3
set label "Hg436" at 436,5
set arrow from 487,0 to 487,255 nohead dashtype 3
set label "Tb487" at 487,5
set arrow from 542,0 to 542,255 nohead dashtype 3
set arrow from 546,0 to 546,255 nohead dashtype 3
set label "Hg546" at 546,5
#set arrow from 577,0 to 577,255 nohead dashtype 3
#set arrow from 580,0 to 580,255 nohead dashtype 3
#set arrow from 584,0 to 584,255 nohead dashtype 3
#set arrow from 587,0 to 587,255 nohead dashtype 3
#set arrow from 593,0 to 593,255 nohead dashtype 3
#set arrow from 599,0 to 599,255 nohead dashtype 3
set arrow from 611,0 to 611,255 nohead dashtype 3
set label "Eu611" at 611,5
plot spectrum using ($1*m+b):2 title snameTitle with lines

pause -1

