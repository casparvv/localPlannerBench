set term postscript eps color size 10, 7 font "RomanSerif.ttf" 14
seriesFolder=ARG1
N=ARG2

inFile0=seriesFolder."resultsTable_fabric_0.csv"
inFile16=seriesFolder."resultsTable_sensorfabric_16.csv"
inFile64=seriesFolder."resultsTable_sensorfabric_64.csv"
inFile256=seriesFolder."resultsTable_sensorfabric_256.csv"
inFile512=seriesFolder."resultsTable_sensorfabric_512.csv"
CompositionTime=seriesFolder."composition_time_total.csv"

set datafile separator ' '
firstrow = system('head -1 '.inFile0)

set tmargin at screen 0.95
set bmargin at screen 0.18
set lmargin at screen 0.14
set style fill solid 0.5 border -1
set style boxplot nooutliers
set style data boxplot
set boxwidth 0.5
set pointsize 0.5
set xtics ('0.0' 1, '0' 2, '16' 3, '64' 4, '256' 5, '512' 6) rotate by 90 font ",55" offset 0,-7.5
set ytics font ",55"
set grid ytics

outFileBox=seriesFolder."/results_comparison_clearance.eps"
set output outFileBox
set yrange [0.0:1.0]
set xlabel "Number of LiDAR rays" font ",60" offset -6.0,-8
set ylabel "Clearance (m)" font ",60" offset -9.0,0
plot inFile0 using (2):2 notitle, inFile16 using (3):2 notitle, inFile64 using (4):2 notitle, inFile256 using (5):2 notitle, inFile512 using (6):2 notitle

outFileBox=seriesFolder."/results_comparison_pathlength.eps"
set output outFileBox
set yrange [10:20]
#set ytics 0,2,20
set xlabel "Number of LiDAR rays" font ",60" offset -6.0,-8
set ylabel "Path length (m)" font ",60" offset -8.0,0
plot inFile0 using (2):3 notitle, inFile16 using (3):3 notitle, inFile64 using (4):3 notitle, inFile256 using (5):3 notitle, inFile512 using (6):3 notitle

outFileBox=seriesFolder."/results_comparison_solving_time.eps"
set output outFileBox
set yrange [0.0:0.015]
set xlabel "Number of LiDAR rays" font ",60" offset -6.0,-8
set ylabel "Solving time (s)" font ",60" offset -12,0
plot inFile0 using (2):4 notitle, inFile16 using (3):4 notitle, inFile64 using (4):4 notitle, inFile256 using (5):4 notitle, inFile512 using (6):4 notitle

outFileBox=seriesFolder."/results_comparison_time2goal.eps"
set output outFileBox
set yrange [0:20]
set xlabel "Number of LiDAR rays" font ",60" offset -6.0,-8
set ylabel "Time to goal (s)" font ",60" offset -8.0,0
plot inFile0 using (2):5 notitle, inFile16 using (3):5 notitle, inFile64 using (4):5 notitle, inFile256 using (5):5 notitle, inFile512 using (6):5 notitle

outFileBox=seriesFolder."/results_comparision_composition_time.eps"
set output outFileBox
set yrange [0.01:100]
set logscale y
set xlabel "Number of LiDAR rays" font ",60" offset -6.0,-8
set ylabel "Composition time (s)" font ",60" offset -11,0
plot CompositionTime using (2):1 notitle, CompositionTime using (3):2 notitle, CompositionTime using (4):3 notitle, CompositionTime using (5):4 notitle, CompositionTime using (6):5 notitle

