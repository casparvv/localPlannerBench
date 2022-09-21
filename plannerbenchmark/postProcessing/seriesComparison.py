import yaml
import os
import re
import csv
import numpy as np

from plannerbenchmark.postProcessing.seriesEvaluation import SeriesEvaluation


class SeriesComparison(SeriesEvaluation):
    """Series comparison between multiple planners."""

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

    def process(self) -> None:
        """Process series, writes results and compares different planners."""
        super().process()
        super().writeResults()
        self.compare()

    def compare(self) -> None:
        """Compares the performance of multiple planners.

        Multiple planners are compared by computing the ratio for all individual
        metrics for every experiment in the series.
        
        To do: it now calculates the average for the metrics per experiment since there are more than 1 experiments. 
         Find a new way to compare them or leave as is.
        """
        self.readResults()
        commonTimeStamps = self.getCasesSolvedByBoth()
        comparedResults = {}
        # averageResults = {}
        for timeStamp in commonTimeStamps:
            # averageResults[timeStamp] = [0, 0, 0]
            # for n_experiment in range(len(self._results)):
            #     averageResults[timeStamp] += self._results[n_experiment][timeStamp]
            # averageResults[timeStamp] = averageResults[timeStamp] / len(self._results)
            comparedResults[timeStamp] = (
                self._results[0][timeStamp] / self._results[1][timeStamp]
            )
        self._results.append(comparedResults)
        # self._results.append(averageResults)

    def writeResults(self, ) -> None:
        """Writes comparison resultTable_comparison.csv-file."""
        resultsTableFile = self._folder + "/resultsTable_comparison.csv"
        with open(resultsTableFile, "w") as file:
            csv_writer = csv.writer(file, delimiter=" ")
            csv_header = self.filterMetricNames()
            csv_writer.writerow(csv_header)
            for timeStampKey in self._results[2]:
                kpis_timeStamp = self._results[2][timeStampKey].tolist()
                csv_writer.writerow([timeStampKey] + kpis_timeStamp)

    def getCasesSolvedByBoth(self) -> list:
        """Gets timestamps of all cases that were solved by both solvers.

        Returns
        -------
        list of str
            List containing all time stamps as strings that were solved by both methods.

        """
        # To do: currently compares two methods which also works fine for more methods though.
        res0 = set(self._results[0])
        res1 = set(self._results[1])
        commonTimeStamps = []
        for timeStamp in res0.intersection(res1):
            commonTimeStamps.append(timeStamp)
        return commonTimeStamps

    def readResults(self):
        """Reads results from previous evaluations."""
        plannerNames = self.getPlannerNames()
        self._results = []
        for i in range(len(plannerNames)):
            plannerDict = {}
            resultsTableFile = (
                self._folder + "/resultsTable_" + plannerNames[i] + ".csv"
            )
            with open(resultsTableFile, mode="r") as inp:
                reader = csv.reader(inp, delimiter=" ")
                next(reader)
                for rows in reader:
                    values = np.array([float(x) for x in rows[1:]])
                    plannerDict[rows[0]] = values
            self._results.append(plannerDict)
