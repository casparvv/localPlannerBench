set term postscript eps color size 7.0, 7.0 font "RomanSerif.ttf" 14
seriesFolder=ARG1
inFile=seriesFolder."successTableOrdered.csv"
outFileHist=seriesFolder."/success.eps"

set output outFileHist
set datafile separator ' '
set bmargin at screen 0.18
set tmargin at screen 0.72
set rmargin at screen 0.9

set style fill solid 0.5 border -1
set style data histogram
set style histogram rowstacked
set border 9
set boxwidth 0.5
set xtics ('1' 0, '2' 1, '4' 2, '8' 3, '16' 4, '32' 5, '64' 6, '128' 7, '256' 8, '512' 9, '1024' 10, '2048' 11) scale 1.0 font ',55' rotate by 90 offset 0, -7.5 nomirror
unset ytics
set xlabel "Number of LiDAR rays" font ",60" offset 0,-8
nbPlanner=12
nbCases=30
set xrange [-0.5:nbPlanner - 0.5]
set yrange [0:2 * nbCases]
set y2range [0:1.2 * nbCases]
set y2tics nomirror font ',55'
set y2tics 0,nbCases/5,nbCases rotate by 90 offset 1.5,-2.0
set y2label '#Cases' font ',55' offset 2.5,0

set key autotitle columnhead
unset key

x = -0.2
dx = 0.1 * nbPlanner
x2 = x + 2 * dx
x3 = x2 + 2 * dx
y = 1.05 * nbCases
dy = 0.05 * nbCases

set label 2 'Success' at x,y+dy rotate by 90 offset 1*nbPlanner + 1*dx - 8,15 font ',55'
set object rect from x,y+22 to x+dx,y+dy+22 fc rgb 'white' fs transparent solid 0.5
set label 3 'Collision' at x2 - 1,y+dy rotate by 90 offset 1*nbPlanner + 1*dx - 8,15 font ',55'
set object rectangle from x2 - 1,y+22 to x2+dx - 1,y+dy+22 fc rgb 'black' fs transparent solid 0.5
set label 4 'Not Reached' at x3 - 2,y+dy rotate by 90 offset 1*nbPlanner + 1*dx - 8,15 font ',55'
set object rectangle from x3 - 2,y+22 to x3+dx - 2,y+dy+22 fc rgb 'gray' fs transparent solid 0.5
plot inFile using 4 notitle lc rgbcolor 'white' axes x1y2, \
   '' using 3 notitle lc rgb 'black' axes x1y2, \
   '' using 2 notitle lc rgb 'gray' axes x1y2
