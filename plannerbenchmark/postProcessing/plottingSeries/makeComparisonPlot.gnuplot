set term postscript eps color size 10, 7 font "RomanSerif.ttf" 14
seriesFolder=ARG1
planner1Type=ARG2
planner2Type=ARG3
N=ARG4

inFile1=seriesFolder."resultsTable_sensorfabric_1.csv"
inFile2=seriesFolder."resultsTable_sensorfabric_2.csv"
inFile4=seriesFolder."resultsTable_sensorfabric_4.csv"
inFile8=seriesFolder."resultsTable_sensorfabric_8.csv"
inFile16=seriesFolder."resultsTable_sensorfabric_16.csv"
inFile32=seriesFolder."resultsTable_sensorfabric_32.csv"
inFile64=seriesFolder."resultsTable_sensorfabric_64.csv"
inFile128=seriesFolder."resultsTable_sensorfabric_128.csv"
inFile256=seriesFolder."resultsTable_sensorfabric_256.csv"
inFile512=seriesFolder."resultsTable_sensorfabric_512.csv"
inFile1024=seriesFolder."resultsTable_sensorfabric_1024.csv"
inFile2048=seriesFolder."resultsTable_sensorfabric_2048.csv"
outFileBox=seriesFolder."/results_comparison_pathlength.eps"
set output outFileBox

set datafile separator ' '
firstrow = system('head -1 '.inFile1)

set style fill solid 0.5 border -1
set style boxplot nooutliers
set style data boxplot
set boxwidth 0.5
set pointsize 0.5
set xtics ('0.0' 1, '1' 2, '2' 3, '4' 4, '8' 5, '16' 6, '32' 7, '64' 8, '128' 9, '256' 10, '512' 11, '1024' 12, '2048' 13)
set grid ytics
set xlabel "Number of LiDAR rays" font ",25"
set ylabel "Path length (m)" font ",25"

plot inFile1 using (2):2 notitle, inFile2 using (3):2 notitle, inFile4 using (4):2 notitle, inFile8 using (5):2 notitle, inFile16 using (6):2 notitle, inFile32 using (7):2 notitle, inFile64 using (8):2 notitle, inFile128 using (9):2 notitle, inFile256 using (10):2 notitle, inFile512 using (11):2 notitle, inFile1024 using (12):2 notitle, inFile2048 using (13):2 notitle


outFileBox=seriesFolder."/results_comparison_time2goal.eps"
set output outFileBox

set xlabel "Number of LiDAR rays" font ",25"
set ylabel "Time to goal (s)" font ",25"

plot inFile1 using (2):3 notitle, inFile2 using (3):3 notitle, inFile4 using (4):3 notitle, inFile8 using (5):3 notitle, inFile16 using (6):3 notitle, inFile32 using (7):3 notitle, inFile64 using (8):3 notitle, inFile128 using (9):3 notitle, inFile256 using (10):3 notitle, inFile512 using (11):3 notitle, inFile1024 using (12):3 notitle, inFile2048 using (13):3 notitle
