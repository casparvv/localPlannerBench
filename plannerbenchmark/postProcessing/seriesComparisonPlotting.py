import subprocess
import os
import re

from plannerbenchmark.generic.experiment import Experiment

pkg_path = os.path.dirname(__file__) + "/../postProcessing/"


class SeriesComparisonPlotting(object):
    """Plotting wrapper for series comparisons."""

    def __init__(self, folder: str, nbMetrics: int):
        self._folder: str = folder
        self._nbMetrics: int = nbMetrics

    def getPlannerNames(self) -> list:
        """Gets planner names."""
        plannerNames = set()
        folderNames = [os.path.split(folderName)[-1] for folderName in list(filter(os.path.isdir, list(map(lambda x: os.path.join(self._folder, x), os.listdir(self._folder)))))]
        pattern = re.compile(r"(\D*)_\d{8}_\d{6}")
        if not re.match(pattern, folderNames[0]):
            pattern = re.compile(r"(\D*)(_\d*)_\d{8}_\d{6}")
        for fname in folderNames:
            match = re.match(pattern, fname)
            if match:
                plannerNames.add(match.group(1) + match.group(2))
        return sorted(list(plannerNames))
        # """Gets planner names."""
        # plannerNames = set()
        # pattern = re.compile(r"(\D*)_\d{8}_\d{6}")
        # for fname in os.listdir(self._folder):
        #     match = re.match(pattern, fname)
        #     if match:
        #         plannerNames.add(match.group(1))
        # return sorted(list(plannerNames))

    def plot(self) -> None:
        """Call the correct gnuplot script.

        The gnuplot scripts are called using subprocess.Popen to avoid
        additional libraries. Depending on the robot type, the gnuplot scripts
        take a different number of arguments. Output from the gnuplot scripts
        is passed to the subprocess.PIPE.
        """
        curPath = os.path.dirname(os.path.abspath(__file__)) + "/"
        curPath = pkg_path
        createPlotFolder = curPath + "plottingSeries"
        plot_shell_script = "./createComparisonPlot"
        # Select Exp plotting script, remove for normal usage
        createPlotFolder = curPath + "plottingSensorFabric"
        plot_shell_script = "./createComparisonPlotExp4"
        
        plannerNames = self.getPlannerNames()
        subprocess.Popen(
            [
                plot_shell_script,
                self._folder,
                str(self._nbMetrics),
            ],
            cwd=createPlotFolder,
            stdout=subprocess.PIPE,
        ).wait()
