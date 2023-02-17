set term postscript eps color size 10, 7 font "RomanSerif.ttf" 14
seriesFolder=ARG1
N=ARG2

inFile1=seriesFolder."resultsTable_sensorfabric_1.csv"
inFile32=seriesFolder."resultsTable_sensorfabric_32.csv"
inFile64=seriesFolder."resultsTable_sensorfabric_64.csv"
inFile128=seriesFolder."resultsTable_sensorfabric_128.csv"
inFile256=seriesFolder."resultsTable_sensorfabric_256.csv"

set datafile separator ' '
firstrow = system('head -1 '.inFile1)

set tmargin at screen 0.95
set bmargin at screen 0.18
set lmargin at screen 0.14
set style fill solid 0.5 border -1
set style boxplot nooutliers
set style data boxplot
set boxwidth 0.5
set pointsize 0.5
set xtics ('0.0' 1, '1' 2, '32' 3, '64' 4, '128' 5, '256' 6) font ",60" offset 0,-2.5
set ytics font ",60"
set grid ytics

outFileBox=seriesFolder."/results_comparison_clearance.eps"
set output outFileBox
set yrange [0.0:1.0]
set xlabel "Number of LiDAR rays" font ",65" offset -6.0,-6
set ylabel "Clearance (m)" font ",65" offset -11,0
plot inFile1 using (2):2 notitle, inFile32 using (3):2 notitle, inFile64 using (4):2 notitle, inFile128 using (5):2 notitle, inFile256 using (6):2 notitle

