#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 17:55:52 2019

@author: mert
"""

from pyomo.environ import *
from ReferenceModel import model # import model
import pandas as pd

model = model.create_instance('/home/mert/optimization/pyomo_code/Stochastic/trial_two/scenariodata/Scenario1.dat')
solver = SolverFactory('gurobi')
solver.solve(model) # solve
