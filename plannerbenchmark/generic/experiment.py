import yaml
import csv
import gym
import numpy as np
import casadi as ca

from urdfenvs.robots.generic_urdf import GenericUrdfReacher
from urdfenvs.urdf_common.urdf_env import UrdfEnv

from urdfenvs.sensors.lidar import Lidar

from forwardkinematics.fksCommon.fk_creator import FkCreator
from mpscenes.goals.goal_composition import GoalComposition
from mpscenes.obstacles.dynamic_sphere_obstacle import DynamicSphereObstacle

class ExperimentIncompleteError(Exception):
    pass


class InvalidInitStateError(Exception):
    pass


class ExperimentInfeasible(Exception):
    pass


class Experiment(object):
    def __init__(self, setupFile):
        self._setupFile = setupFile
        self._required_keys = [
            "T",
            "dt",
            "env",
            "n",
            "goal",
            "initState",
            "robot_type",
            "limits",
            "obstacles",
            "r_body",
            "selfCollision",
            "dynamic",
        ]
        self.parseSetup()
        self._fk = FkCreator(self.robotType(), self.n()).fk()

    def parseSetup(self):
        with open(self._setupFile, "r") as setupStream:
            self._setup = yaml.safe_load(setupStream)
        self.checkCompleteness()
        self._motionPlanningGoal = GoalComposition(name="mpg", content_dict=self._setup['goal'])
        self.parseObstacles()

    def parseObstacles(self):
        number_of_obstacles = 19
        self._obstacles = []
        
        if number_of_obstacles > 0:
            all_dynamicObstDict = {}
            all_dynamicSphereObst = {}
            
            rng = np.random.default_rng()
            xs = rng.uniform(low=-4.0, high=4.0, size=number_of_obstacles).tolist()
            ys = rng.uniform(low=1.5, high=8.0, size=number_of_obstacles).tolist()
            ms = rng.uniform(low=-1.2, high=1.2, size=number_of_obstacles).tolist()
            
            for n_ob in range(number_of_obstacles):
                all_dynamicObstDict[f'dynamicObstDict_{n_ob}'] = {
                        "type": "sphere",
                        "geometry": {"trajectory": [f"{xs[n_ob]} + {ms[n_ob]}*t", f"{ys[n_ob]} + {ms[n_ob]}*t", "0.0"], "radius": 0.5},
                }
                all_dynamicSphereObst[f'dynamicSphereObst_{n_ob}'] = DynamicSphereObstacle(
                        name=f"simpleSphere_{n_ob}", content_dict=all_dynamicObstDict[f'dynamicObstDict_{n_ob}']
                )
                self._obstacles.append(all_dynamicSphereObst[f'dynamicSphereObst_{n_ob}'])

            dso_dict = {
                        "type": "sphere",
                        "geometry": {"trajectory": ["0.2", "2 - 1.2*t", "0.0"], "radius": 0.5},
                }
            dso = DynamicSphereObstacle(
                    name="simpleSphere_test", content_dict=dso_dict
            )
            self._obstacles.append(dso)
        else:
            if self._setup["obstacles"]:
                self._obstacleCreator = ObstacleCreator()
                for obst in self._setup["obstacles"]:
                    obstData = self._setup["obstacles"][obst]
                    obstType = obstData['type']
                    obstName = obst
                    self._obstacles.append(self._obstacleCreator.create_obstacle(obstType, obstName, obstData))

    def dynamic(self):
        return self._setup['dynamic']

    def selfCollisionPairs(self):
        if self._setup['selfCollision']['pairs']:
            return self._setup["selfCollision"]["pairs"]
        else:
            return []

    def rBody(self):
        return self._setup["r_body"]

    def fk(self, q, n, positionOnly=False):
        return self._fk.fk(q, n, positionOnly=positionOnly)

    def evaluate(self, t):
        evalObsts = self.evaluateObstacles(t=t)
        evalGoal = self._motionPlanningGoal.evaluate(t=t)
        return evalGoal + evalObsts

    def evaluateObstacles(self, t):
        evals = np.zeros((len(self._obstacles), 3))
        i = 0
        for obst in self._obstacles:
            evals[i] = obst.traj().evaluate(t=t)[0]
            i += 1
        return evals

    def robotType(self):
        return self._setup["robot_type"]

    def n(self):
        return self._setup["n"]

    def T(self):
        return self._setup["T"]

    def dt(self):
        return self._setup["dt"]

    def envName(self):
        return self._setup["env"]

    def obstacles(self):
        return self._obstacles

    def limits(self):
        low = np.array(self._setup["limits"]["low"])
        high = np.array(self._setup["limits"]["high"])
        return low, high

    def initState(self):
        try:
            q0 = np.array([float(x) for x in self._setup["initState"]["q0"]])
            q0dot = np.array([float(x) for x in self._setup["initState"]["q0dot"]])
        except:
            raise InvalidInitStateError("Initial state could not be parsed")
        """
        if q0.size != self.n() or q0dot.size != self.n():
            raise InvalidInitStateError("Initial state of wrong dimension")
        """
        return (q0, q0dot)

    def goal(self):
        return self._motionPlanningGoal

    def primeGoal(self, **kwargs):
        return self._motionPlanningGoal.primary_goal()
        if 't' in kwargs:
            return self._motionPlanningGoal.evaluatePrimeGoal(kwargs.get('t'))
        else:
            return self._motionPlanningGoal.primary_goal()

    def evaluatePrimeGoal(self, t):
        return self.primeGoal().position(t=t)

    def getDynamicGoals(self):
        return self._motionPlanningGoal.dynamicGoals()

    def env(self, render=False):
        if self.robotType() == 'planarArm':
            return gym.make(self.envName(), render=render, n=self.n(), dt=self.dt())
        if self.robotType() == 'pointRobotUrdf':
            robots = [
                    GenericUrdfReacher(urdf="pointRobot.urdf", mode="acc"),
            ]
            env: UrdfEnv = gym.make(
                    "urdf-env-v0",
                    dt=0.01, robots=robots, render=render
            )
            return env
        else:
            return gym.make(self.envName(), render=render, dt=self.dt())

    def showLidar(self, env, sensor_data, q, body_ids_old, number_lidar_rays, show_lidar_mode):
        if show_lidar_mode == "rays_spheres":
            body_ids = env.show_lidar(sensor_data, q, body_ids_old, number_lidar_rays)
        if show_lidar_mode == "spheres":
            body_ids = env.show_lidar_spheres(sensor_data, q, body_ids_old, number_lidar_rays)
        return body_ids
    
    def addScene(self, env, nb_rays=0):
        name_exp = "a4"
        if name_exp == "a1":
            env.add_walls(dim=np.array([0.2, 9.2, 0.5]), poses_2d=[[-4.5, 3.5, 0], [4.5, 3.5, 0], [0, -1, np.pi/2], [0, 8, np.pi/2]])
        if name_exp == "a2":
            env.add_walls(dim=np.array([0.2, 3.2, 0.5]), poses_2d=[[0, -1, np.pi/2]])
            env.add_walls(dim=np.array([0.2, 10, 0.5]), poses_2d=[[-1.5, 4, 0]])
            env.add_walls(dim=np.array([0.2, 7, 0.5]), poses_2d=[[1.5, 2.5, 0]])
            env.add_walls(dim=np.array([0.2, 8.2, 0.5]), poses_2d=[[2.5, 9, np.pi/2]])
            env.add_walls(dim=np.array([0.2, 2.2, 0.5]), poses_2d=[[2.5, 6, np.pi/2]])
            env.add_walls(dim=np.array([0.2, 6, 0.5]), poses_2d=[[6.5, 6, 0]])
            env.add_walls(dim=np.array([0.2, 3, 0.5]), poses_2d=[[3.5, 4.5, 0]])
            env.add_walls(dim=np.array([0.2, 3.2, 0.5]), poses_2d=[[5, 3, np.pi/2]]) 
        if name_exp == "a3":
            env.add_walls(dim=np.array([0.2, 3.2, 0.5]), poses_2d=[[0, -1, np.pi/2]])
            env.add_walls(dim=np.array([0.2, 16.2, 0.5]), poses_2d=[[-1.5, 7, 0]])
            env.add_walls(dim=np.array([0.2, 16.2, 0.5]), poses_2d=[[1.5, 7, 0]])
            env.add_walls(dim=np.array([0.2, 3.2, 0.5]), poses_2d=[[0, 15, np.pi/2]])
        for obst in self._obstacles:
            env.add_obstacle(obst)
        try:
            env.add_goal(self.goal())
        except Exception as e:
            print(e)
        if nb_rays > 0:
            lidar = Lidar(4, nb_rays=nb_rays, raw_data=False)
            env.add_sensor(lidar, robot_ids=[0])
            env.set_spaces()

    def shuffleInitConfiguration(self):
        q0_new = np.random.uniform(low=self.limits()[0], high=self.limits()[1])
        self._setup["initState"]["q0"] = q0_new.tolist()

    def shuffleObstacles(self):
        self._obstacles = []
        for i in range(self._setup["randomObstacles"]["number"]):
            obstData = self._setup["obstacles"][f"obst{str(i)}"]
            obstType = obstData['type']
            obstName = f"obst{str(i)}"
            randomObst = self._obstacleCreator.create_obstacle(obstType, obstName, obstData)
            randomObst.shuffle()
            self._obstacles.append(randomObst)

    def shuffle(self, random_obst, random_init, random_goal):
        if random_goal:
            self._motionPlanningGoal.shuffle()
        if random_obst:
            self.shuffleObstacles()
        if random_init:
            self.shuffleInitConfiguration()
        self.parseObstacles()
        return

    def checkCompleteness(self):
        incomplete = False
        missingKeys = ""
        for key in self._required_keys:
            if key not in self._setup.keys():
                incomplete = True
                missingKeys += key + ", "
        if incomplete:
            raise ExperimentIncompleteError("Missing keys: %s" % missingKeys[:-2])

    def checkFeasibility(self, checkGoalReachible):
        for o in self.obstacles():
            for i in range(1, self.n() + 1):
                fk = self.fk(self.initState()[0], i, positionOnly=True)
                if self.robotType() == 'boxer':
                    fk = fk[0:2]
                dist_initState = np.linalg.norm(np.array(o.position()) - fk)
                if dist_initState < (o.radius() + self.rBody()):
                    raise ExperimentInfeasible("Initial configuration in collision")
            if not self.dynamic() and len(o.position()) == len(self.primeGoal().position()):
                dist_goal = np.linalg.norm(np.array(o.position()) - self.primeGoal().position())
                if dist_goal < (o.radius() + self.rBody()):
                    raise ExperimentInfeasible("Goal in collision")
        for pair in self.selfCollisionPairs():
            fk1 = self.fk(self.initState()[0], pair[0], positionOnly=True)
            fk2 = self.fk(self.initState()[0], pair[1], positionOnly=True)
            dist_initState = np.linalg.norm(fk1 - fk2)
            if dist_initState < (2 * self.rBody()):
                raise ExperimentInfeasible(
                    "Initial configuration in self collision"
                )
        if self.robotType() == "planarArm":
            if np.linalg.norm(np.array(self.primeGoal().position())) > self.n():
                raise ExperimentInfeasible("Goal unreachible")

    def save(self, folderPath):
        self._setup["goal"] = self._motionPlanningGoal.dict()
        obstsDict = {}
        obstFile = folderPath + "/obst"
        initStateFilename = folderPath + "/initState.csv"
        for i, obst in enumerate(self._obstacles):
            obstsDict[obst.name()] = obst.dict()
            obst.csv(obstFile + "_" + str(i) + ".csv")
        self._setup["obstacles"] = obstsDict
        with open(folderPath + "/exp.yaml", "w") as file:
            yaml.dump(self._setup, file)
        with open(initStateFilename, "w") as file:
            csv_writer = csv.writer(file, delimiter=",")
            csv_writer.writerow(self.initState()[0])

