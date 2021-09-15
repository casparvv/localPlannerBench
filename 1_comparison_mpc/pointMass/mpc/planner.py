import time
import numpy as np
from numpy import sin, cos
import casadi as ca
import yaml

import forcespro.nlp

import os
import sys
path_name = os.path.dirname(os.path.realpath(__file__))
sys.path.append(path_name)
from createMPCSolver import getParameters

from createMPCSolver import eval_obj, eval_objN, eval_ineq, continuous_dynamics


from solverPlot import SolverPlot
from robotPlot import RobotPlot
from obstacle import Obstacle
from splineFunctions import project

class MPCPlanner(object):

    def __init__(self, setupFile):
        # nbObst=5, wx=0.5, wvel=1, wu=1, ws=1e8, N=80, dt=0.05, interval=1):
        self.parseSetup(setupFile)
        self._H = self._params['H']
        self._nbObst = self._params['obst']['nbObst']
        self._m = 2
        self._n = 2
        self._paramMap, self._npar, self._nx, self._nu, _, self._ns = getParameters(2, 2, self._nbObst)
        self._dt = self._params['dt']
        self._interval = self._params['interval']
        self._wx = self._params['weights']['wx']
        self._wvel = self._params['weights']['wvel']
        self._ws = self._params['weights']['ws']
        self._wu = self._params['weights']['wu']
        dt_str = str(self._dt).replace('.', '')
        mpcFileName = 'mpc/solver_' + dt_str + '_N' + str(self._H)
        self._mpcSolver = forcespro.nlp.Solver.from_directory(mpcFileName)
        self._x0 = np.zeros(shape=(self._H, self._nx+self._nu+self._ns))
        self._xinit = np.zeros(self._nx)
        self._slack = 0.0
        self._x0[-1, -1] = 0.1
        self._params = np.zeros(shape=(self._npar * self._H), dtype=float)
        for i in range(self._H):
            self._params[
                [self._npar * i + val for val in self._paramMap["w"]]
            ] = self._wx
            self._params[
                [self._npar * i + val for val in self._paramMap["wvel"]]
            ] = self._wvel
            self._params[
                [self._npar * i + val for val in self._paramMap["wu"]]
            ] = self._wu
            self._params[
                [self._npar * i + val for val in self._paramMap["ws"]]
            ] = self._ws

    def parseSetup(self, setupFile):
        with open(setupFile, 'r') as stream:
            self._params = yaml.safe_load(stream)

    def addGoal(self, goal):
        for i in range(self._H):
            for j in range(self._m):
                self._params[self._npar * i + self._paramMap["g"][j]] = goal[j]

    def addObstacles(self, obsts):
        for i in range(self._H):
            for j in range(self._nbObst):
                if j < len(obsts):
                    obst = obsts[j]
                else:
                    obst = Obstacle(np.array([-10.0, 10.0]), -1.0)
                self._params[self._npar * i + self._paramMap["obst"][j*3 + 0]] = obst.x()[0]
                self._params[self._npar * i + self._paramMap["obst"][j*3 + 1]] = obst.x()[1]
                self._params[self._npar * i + self._paramMap["obst"][j*3 + 2]] = obst.r()

    def shiftHorizon(self, output, ob):
        nvar = self._nx + self._nu + self._ns
        for key in output.keys():
            stage = int(key[-2:])
            if stage == 1:
                continue
            self._x0[stage-2,0:len(output[key])] = output[key]

    def setX0(self, xinit):
        for i in range(self._H):
            self._x0[i][0:self._nx] = xinit

    def solve(self, ob):
        #print("Observation : " , ob[0:self._nx])
        self._xinit = ob[0:self._nx]
        action = np.zeros(self._nu)
        problem = {}
        #problem["ToleranceStationarity"] = 1e-7
        #problem["ToleranceEqualities"] = 1e-7
        #problem["ToleranceInequalities"] = 1e-7
        #problem["SolverTimeout"] = 0.0001
        #problem["ToleranceComplementarity"] = 1e-5
        problem["xinit"] = self._xinit
        #problem["x0"] = self._x0.flatten()[:-self._nu]
        self._x0[0][0:self._nx] = self._xinit
        self.setX0(self._xinit)
        problem["x0"] = self._x0.flatten()[:]
        problem["all_parameters"] = self._params
        nbPar = int(len(self._params)/self._H)
        # debug
        """
        z = np.concatenate((xinit, np.array([self._slack, 0, 0])))
        p = self._params[0:nbPar]
        J = eval_obj(z, p)
        #print("J : ", J)
        ineq = eval_ineq(z, p)
        #print("ineq : ", ineq)
        for i in range(self._H):
            z = self._x0[i]
            ineq = eval_ineq(z, p)
            #print("ineq : ", ineq)
        """
        output, exitflag, info = self._mpcSolver.solve(problem)
        if exitflag < 0 :
            print(exitflag)
        action = output["x01"][-self._nu:]
        self._slack = output["x01"][self._nx]
        if self._slack > 1e-3:
            print("slack : ", self._slack)
        #print('action : ', action)
        #print("prediction : ", output["x02"][0:self._nx])
        self.shiftHorizon(output, ob)
        return action, info

    def concretize(self):
        self._actionCounter = self._interval

    def computeAction(self, q, qdot):
        ob = np.concatenate((q, qdot))
        if self._actionCounter >= self._interval:
            self._action, info = self.solve(ob)
            self._actionCounter = 1
        else:
            self._actionCounter += 1
        return self._action


