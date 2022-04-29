# General dependencies
from dataclasses import dataclass, field
from typing import Dict
import casadi as ca
import numpy as np

# Dependencies for this specific planner
from fabrics.planner.fabricPlanner import DefaultFabricPlanner
from fabrics.planner.nonHolonomicPlanner import DefaultNonHolonomicPlanner
from fabrics.planner.default_energies import CollisionLagrangian, ExecutionLagrangian
from fabrics.planner.default_maps import (
    CollisionMap,
    LowerLimitMap,
    UpperLimitMap,
    SelfCollisionMap,
)
from fabrics.planner.default_leaves import defaultAttractor, defaultDynamicAttractor
from fabrics.planner.default_geometries import (
    CollisionGeometry,
    GoalGeometry,
    LimitGeometry,
)
from fabrics.diffGeometry.analyticSymbolicTrajectory import AnalyticSymbolicTrajectory
from fabrics.diffGeometry.diffMap import DifferentialMap, RelativeDifferentialMap
from fabrics.diffGeometry.energized_geometry import WeightedGeometry

# Motion planning scenes
from MotionPlanningEnv.dynamicSphereObstacle import DynamicSphereObstacle
from MotionPlanningEnv.sphereObstacle import SphereObstacle

# Dependencies on plannerbenchmark
from plannerbenchmark.generic.planner import Planner, PlannerConfig

@dataclass
class FabricConfig(PlannerConfig):
    m_base: float = 0.2
    m_ratio: float = 1.0
    obst: Dict[str, float] = field(default_factory = lambda: ({'exp': 1.0, 'lam': 1.0}))
    selfCol: Dict[str, float] = field(default_factory = lambda: ({'exp': 1.0, 'lam': 1.0}))
    attractor: Dict[str, float] = field(default_factory = lambda: ({'k_psi': 3.0}))
    speed: Dict[str, float] = field(default_factory = lambda : ({'ex_factor': 1.0}))
    dynamic: bool = False
    limits: Dict[str, float] = field(default_factory = lambda: ({'exp': 1.0, 'lam': 1.0}))
    damper: Dict[str, object] = field(default_factory = lambda :({'r_d': 0.8, 'b': [0.1, 6.5]}))
    l_offset: float = 0.2
    m_arm: float = 1.0
    m_rot: float = 1.0


class FabricPlanner(Planner):

    def __init__(self, exp, **kwargs):
        super().__init__(exp, **kwargs)
        self._config = FabricConfig(**kwargs)
        self.reset()


    def reset(self):
        if self._exp.robotType() in ['groundRobot', 'boxer', 'albert']:
            self._planner = DefaultNonHolonomicPlanner(
                    self.config.n, 
                    m_rot=self.config.m_rot,
                    l_offset=self.config.l_offset,
                    m_arm=self.config.m_arm,
                    m_ratio=self.config.m_ratio,
                    m_base=self.config.m_base,
                    debug=False
            )
        else:
            self._planner = DefaultFabricPlanner(self.config.n, m_base=self.config.m_base, debug=False)
        self._q, self._qdot = self._planner.var()

    def setObstacles(self, obsts, r_body):
        x = ca.SX.sym("x", 1)
        xdot = ca.SX.sym("xdot", 1)
        lag_col = CollisionLagrangian(x, xdot)
        geo_col = CollisionGeometry(
            x, xdot, exp=self.config.obst['exp'], lam=self.config.obst["lam"]
        )
        for i, obst in enumerate(obsts):
            m_obst = obst.dim()
            if isinstance(obst, DynamicSphereObstacle):
                refTraj_i = AnalyticSymbolicTrajectory(ca.SX(np.identity(m_obst)), m_obst, traj=obst.traj())
                x_col = ca.SX.sym("x_col", m_obst)
                xdot_col = ca.SX.sym("xdot_col", m_obst)
                x_rel = ca.SX.sym("x_rel", m_obst)
                xdot_rel = ca.SX.sym("xdot_rel", m_obst)
            for j in range(1, self.config.n + 1):
                if self._exp.robotType() == "pointRobot" and j == 1:
                    continue
                if self._exp.robotType() == "groundRobot" and j == 1:
                    continue
                fk = self._exp.fk(self._q, j, positionOnly=True)
                if self._exp.robotType() == 'boxer':
                    fk = fk[0:2]
                if isinstance(obst, DynamicSphereObstacle):
                    phi_n = ca.norm_2(x_rel) / (obst.radius() + r_body) - 1
                    dm_n = DifferentialMap(phi_n, q=x_rel, qdot=xdot_rel)
                    dm_rel = RelativeDifferentialMap(q=x_col, qdot=xdot_col, refTraj =refTraj_i)
                    dm_col = DifferentialMap(fk, q=self._q, qdot=self._qdot)
                    eg = WeightedGeometry(g=geo_col, le=lag_col)
                    eg_n = eg.pull(dm_n)
                    eg_rel = eg_n.pull(dm_rel)
                    self._planner.addWeightedGeometry(dm_col, eg_rel)
                    #self._planner.addGeometry(dm_col, lag_col.pull(dm_n).pull(dm_rel), geo_col.pull(dm_n).pull(dm_rel))
                elif isinstance(obst, SphereObstacle):
                    dm_col = CollisionMap(
                        self._q, self._qdot, fk, obst.position(), obst.radius(), r_body=r_body
                    )
                    self._planner.addGeometry(dm_col, lag_col, geo_col)

    def setSelfCollisionAvoidance(self, r_body):
        if self._exp.robotType() == "pointRobot":
            return
        x = ca.SX.sym("x", 1)
        xdot = ca.SX.sym("xdot", 1)
        lag_selfCol = CollisionLagrangian(x, xdot)
        geo_selfCol = CollisionGeometry(
            x,
            xdot,
            exp=self.config.selfCol['exp'],
            lam=self.config.selfCol['lam'],
        )
        for pair in self._exp.selfCollisionPairs():
            fk_1 = self._exp.fk(self._q, pair[0], positionOnly=True)
            fk_2 = self._exp.fk(self._q, pair[1], positionOnly=True)
            dm_selfCol = SelfCollisionMap(self._q, self._qdot, fk_1, fk_2, r_body)
            self._planner.addGeometry(dm_selfCol, lag_selfCol, geo_selfCol)

    def setJointLimits(self, limits):
        x = ca.SX.sym("x", 1)
        xdot = ca.SX.sym("xdot", 1)
        lag_col = CollisionLagrangian(x, xdot)
        geo_col = LimitGeometry(
            x, xdot, lam=self.config.limits["lam"], exp=self.config.limits["exp"],
        )
        for i in range(self.config.n):
            dm_col = UpperLimitMap(self._q, self._qdot, limits[1][i], i)
            self._planner.addGeometry(dm_col, lag_col, geo_col)
            dm_col = LowerLimitMap(self._q, self._qdot, limits[0][i], i)
            self._planner.addGeometry(dm_col, lag_col, geo_col)

    def setGoal(self, goal):
        for subGoal in goal.subGoals():
            if subGoal.type() == "staticJointSpaceSubGoal":
                fk = self._q[subGoal.indices()]
            else:
                fk_child = self._exp.fk(self._q, subGoal.childLink(), positionOnly=True)[subGoal.indices()]
                fk_parent = self._exp.fk(self._q, subGoal.parentLink(), positionOnly=True)[subGoal.indices()]
                fk = fk_child - fk_parent
            if subGoal.type() == "analyticSubGoal":
                goalSymbolicTraj = AnalyticSymbolicTrajectory(ca.SX(np.identity(subGoal.m())), subGoal.m(), traj=subGoal.traj())
                dm_psi, lag_psi, geo_psi, x_psi, xdot_psi = defaultDynamicAttractor(
                    self._q, self._qdot, fk, goalSymbolicTraj, k_psi=self.config.attractor['k_psi'] * subGoal.weight()
                )
                self._planner.addForcingGeometry(dm_psi, lag_psi, geo_psi, goalVelocity=goalSymbolicTraj.xdot())
            elif subGoal.type() == "splineSubGoal": 
                goalSymbolicTraj = AnalyticSymbolicTrajectory(ca.SX(np.identity(subGoal.m())), subGoal.m(), traj=subGoal.traj())
                dm_psi, lag_psi, geo_psi, x_psi, xdot_psi = defaultDynamicAttractor(
                    self._q, self._qdot, fk, goalSymbolicTraj, k_psi=self.config.attractor['k_psi'] * subGoal.weight()
                )
                self._planner.addForcingGeometry(dm_psi, lag_psi, geo_psi, goalVelocity=goalSymbolicTraj.xdot())
            else:
                dm_psi, lag_psi, geo_psi, x_psi, xdot_psi = defaultAttractor(
                    self._q, self._qdot, subGoal.position(), fk
                )
                geo_psi = GoalGeometry(
                    x_psi, xdot_psi, k_psi=self.config.attractor["k_psi"] * subGoal.weight()
                )
                self._planner.addForcingGeometry(dm_psi, lag_psi, geo_psi)
            if subGoal.isPrimeGoal():
                self._dm_psi = dm_psi
                self._x_psi = x_psi
                self._xdot_psi = xdot_psi

    def concretize(self):
        # execution energy
        exLag = ExecutionLagrangian(self._q, self._qdot)
        self._planner.setExecutionEnergy(exLag)
        # Speed control
        # self._planner.setConstantSpeedControl(beta=2.0)
        ex_factor = self.config.speed["ex_factor"]
        self._planner.setDefaultSpeedControl(
            self._x_psi,
            self._dm_psi,
            exLag,
            ex_factor,
            r_b=self.config.damper["r_d"],
            b=self.config.damper["b"],
        )
        self._planner.concretize()

    def computeAction(self, *args):
        action = self._planner.computeAction(*args)
        if self._planner._debug:
            debugEval = self._planner.debugEval(*args)
            print(debugEval)
        action = np.clip(-np.ones(9), np.ones(9), action)

        return action
