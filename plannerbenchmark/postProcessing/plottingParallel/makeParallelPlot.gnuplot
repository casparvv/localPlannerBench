set term postscript eps color size 10.0, 10.0 font "RomanSerif.ttf" 14
parallelFolder=ARG1
N=ARG2
planner0Type=1
planner1Type=2
planner2Type=4
planner3Type=8
planner4Type=16
planner5Type=32
planner6Type=64
planner7Type=128
planner8Type=256
planner9Type=512
planner10Type=1024
planner11Type=2048

inFile=parallelFolder."resultsTable_sensorfabric_".planner0Type.".csv"

set datafile separator ' '
set bmargin at screen 0.2
set tmargin at screen 0.95

set style fill solid 0.5 border -1
set style data boxplot
set grid y2tics

firstrow = system('head -1 '.inFile)

unset key
unset xtics
set xtics () scale 1.0 font ",35" rotate by 90 out offset -0.5, -18.0

do for [i=2:(N+2)] {
  print i
  metricName = word(firstrow, i)
  outFileBox=parallelFolder."/results_".planner0Type."_".metricName.".eps"
  set output outFileBox
  if (metricName eq "solverTime"){
    set xtics add ("Solver Time [ms]" i);
    set y2tics nomirror font ',35' rotate by 90 out offset 0.5,-2.5
    set y2range [0.6:0.80]
    set y2tics (0.65, 0.7, 0.75)
  }
  if (metricName eq "integratedError") {
    set xtics add ("Summed Error" i);
    set y2range [0.0:0.20]
    set y2tics (0.0, 0.1, 0.15)
  }
  if (metricName eq "pathLength") {
    set xtics add ("Path Length [m]" i);
    set y2range [0.0:20.00]
    set y2tics (0.0, 2.0, 4, 6, 8.0, 10, 12, 14, 16, 18, 20)
    set y2tics nomirror font ',35' rotate by 90 out offset 0.5,-1.0
  }
  if (metricName eq "clearance") {
    set xtics add ("Clearance [m]" i);
    set y2range [0.0:1.00]
    set y2tics (0.0, 0.25, 0.5, 0.75, 1.0)
    set y2tics nomirror font ',35' rotate by 90 out offset 0.5,-2.5
  }
  if (metricName eq "invClearance") {
    set xtics add ("Clearance^{-1} [1/m]" i);
    set y2range [0.0:1.00]
    set y2tics (0.0, 0.25, 0.5, 0.75, 1.0)
    set y2tics nomirror font ',35' rotate by 90 out offset 0.5,-2.5
  }
  if (metricName eq "invDynamicClearance") {
    set xtics add ("Clearance^{-1} [1/m]" i);
    set y2range [0.0:1.00]
    set y2tics (0.0, 0.25, 0.5, 0.75, 1.0)
    set y2tics nomirror font ',35' rotate by 90 out offset 0.5,-2.5
  }
  if (metricName eq "selfClearance") {
    set xtics add ("Self Clearence [m]" i);
  }
  if (metricName eq "time2Goal") {
    set xtics add ("Time to Goal [s]" i);
    set y2range [2.0:30.00]
    set y2tics (2.5, 5.0, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25, 27.5, 30)
    set y2tics nomirror font ',35' rotate by 90 out offset 0.5,-2.0
  }
  colorName = 'gray'
  plot inFile using (i):i lw 2 lc rgb colorName  axes x1y2
}
# plot for [i=2:N] inFile using (i):i lw 2 axes x1y2
