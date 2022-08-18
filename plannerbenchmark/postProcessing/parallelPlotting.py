import subprocess
import os
import re

from plannerbenchmark.generic.experiment import Experiment

pkg_path = os.path.dirname(__file__) + "/../postProcessing/"


class ParallelPlotting(object):
    """Plotting wrapper for parallel comparisons."""

    def __init__(self, folder: str, nbMetrics: int):
        self._folder: str = folder
        self._nbMetrics: int = nbMetrics

    def getPlannerNames(self) -> str:
        """Gets planner names."""
        plannerNames = []
        for fname in os.listdir(self._folder):
            if not os.path.isdir(self._folder + "/" + fname):
                continue
            plannerNames.append(fname)
        plannerNames.sort(key=int)
        plannerNames_string = ""
        for plannerName in plannerNames:
            plannerNames_string += f" {str(plannerName)}"
        return plannerNames_string

    def plot(self) -> None:
        """Call the correct gnuplot script.

        The gnuplot scripts are called using subprocess.Popen to avoid
        additional libraries. Depending on the robot type, the gnuplot scripts
        take a different number of arguments. Output from the gnuplot scripts
        is passed to the subprocess.PIPE.
        """
        curPath = os.path.dirname(os.path.abspath(__file__)) + "/"
        curPath = pkg_path
        createPlotFolder = curPath + "plottingParallel"
        plannerNames = self.getPlannerNames()
        
        subprocess.Popen(
            [
                "./createParallelPlot",
                self._folder,
                str(self._nbMetrics),
            ],
            cwd=createPlotFolder,
            stdout=subprocess.PIPE,
        ).wait()
