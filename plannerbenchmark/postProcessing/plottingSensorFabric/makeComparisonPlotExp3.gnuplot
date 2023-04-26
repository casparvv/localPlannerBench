set term postscript eps color size 10, 7 font "RomanSerif.ttf" 14
seriesFolder=ARG1
N=ARG2

inFile0=seriesFolder."resultsTable_fabric_0.csv"
inFile64=seriesFolder."resultsTable_sensorfabric_64.csv"

set datafile separator ' '
firstrow = system('head -1 '.inFile0)

set tmargin at screen 0.95
set bmargin at screen 0.20
set lmargin at screen 0.14
set style fill solid 0.5 border -1
set style boxplot nooutliers
set style data boxplot
set boxwidth 0.5
set pointsize 0.5

unset xtics
set label 400 "Regular\n\n\n\nfabric" at first 0,0 left font ',70' offset 100,-3.5
set label 401 "DSI\n\n\n\nfabric\n\n\n\n64 rays" at first 1,0 left font ',70' offset 105,-3.5

set ytics font ",70"
set grid ytics

outFileBox=seriesFolder."/results_comparison_clearance.eps"
set output outFileBox
set yrange [0.0:1.0]
set ylabel "Clearance (m)" font ",70" offset -12.0,0
plot inFile0 using (2):2 notitle, inFile64 using (3):2 notitle

unset label
set label 400 "Regular\n\n\n\nfabric" at first 0,0 left font ',70' offset 100,-3
set label 401 "DSI\n\n\n\nfabric\n\n\n\n64 rays" at first 1,0 left font ',70' offset 105,-3

outFileBox=seriesFolder."/results_comparison_pathlength.eps"
set output outFileBox
set yrange [0:20]
set ylabel "Path length (m)" font ",70" offset -12.0,0
plot inFile0 using (2):3 notitle, inFile64 using (3):3 notitle

unset label
set label 400 "Regular\n\n\n\nfabric" at first 0,0 left font ',70' offset 100,-3
set label 401 "DSI\n\n\n\nfabric\n\n\n\n64 rays" at first 1,0 left font ',70' offset 105,-3

outFileBox=seriesFolder."/results_comparison_time2goal.eps"
set output outFileBox
set yrange [0:10]
set ylabel "Time to goal (s)" font ",70" offset -11.0,0
plot inFile0 using (2):4 notitle, inFile64 using (3):4 notitle

