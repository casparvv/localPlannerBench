set term postscript eps color size 7.0, 7.0 font "RomanSerif.ttf" 14
seriesFolder=ARG1
inFile=seriesFolder."successTableOrdered.csv"
outFileHist=seriesFolder."/success.eps"

set output outFileHist
set datafile separator ' '
set bmargin at screen 0.25
set tmargin at screen 0.70
set rmargin at screen 0.9

set style fill solid 0.5 border -1
set style data histogram
set style histogram rowstacked
set border 9
set boxwidth 0.5

unset xtics
set label 100 "Regular\n\n\nfabric" at first 0,0 left font ',55' rotate by 90 offset -2,-15
set label 101 "DSI\n\n\nfabric\n\n\n64 rays" at first 1,0 left font ',55' rotate by 90 offset -4,-15

unset ytics
nbPlanner=2
nbCases=30
set xrange [-0.5:nbPlanner - 0.5]
set yrange [0:2 * nbCases]
set y2range [0:1.2 * nbCases]
set y2tics nomirror font ',55'
set y2tics 0,nbCases/5,nbCases rotate by 90 offset 1.5,-2.0
set y2label '#Cases' font ',55' offset 2.5,0

set key autotitle columnhead
unset key

x = -0.15
y = 2 * nbCases

set label 2 'Success' at x,y rotate by 90 font ',55'
set object rect from x-0.1,y-5 to x+0.1,y-2 fc rgb 'white' fs transparent solid 0.5
set label 3 'Collision' at x+0.25,y rotate by 90 font ',55'
set object rect from x+0.15,y-5 to x+0.35,y-2 fc rgb 'black' fs transparent solid 0.5
set label 4 'Not Reached' at x+0.50,y rotate by 90 font ',55'
set object rect from x+0.40,y-5 to x+0.60,y-2 fc rgb 'gray' fs transparent solid 0.5
plot inFile using 4 notitle lc rgbcolor 'white' axes x1y2, \
   '' using 3 notitle lc rgb 'black' axes x1y2, \
   '' using 2 notitle lc rgb 'gray' axes x1y2
