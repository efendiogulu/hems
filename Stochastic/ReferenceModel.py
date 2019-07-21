#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 14 14:53:36 2019

@author: mert
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 22:51:12 2018

@author: mert
"""

from pyomo.environ import *
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import os
import pandas
import numpy
import datetime as dt
from dateutil.relativedelta import *
import xlsxwriter

#Model Decleration
model = AbstractModel()

#####################Objective Function Selection#####################################
"""                                                                                  # 
    The objective function must be entered depending on user choice                  #
                                                                                     #
    Firstly, the multi objective selection must be made.                             #
                                                                                     #
    multi_objective_selection = True    #for multi-objective optimization            #
                                False   #for non-multi-objective optimization        #
                                                                                     #
                                                                                     #
    Secondly, desired the objective must be defined.                                 #
    objective_function = 'energy'               #for energy usage optimization       #
                         'cost'                 #for energy cost optimization        #
                         'income'               #for income optimization             #
                         'no_v2h'               #for no vehicle to home              #
                         'self_consumption'     #for increasing the self comsumption #
                          self_consumption stops at 123 no_v2h 158                   #
                                                                                     #
    v2h_selection =      'no_v2h'               #for no vehicle to home              #
                         'v2h'                  #for enablingthe vehicle to home     #
"""                                                                                  #
                                                     #
######################################################################################

global constraint_starter
global vehicle_charge_deadline
constraint_starter = []
v2h_selection = 'v2h'


rolling_horizon_range = range(24)
#model.RH = Set(initialize=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23], ordered = True) # Modelset initialization
model.RH = Set(ordered = True) 

model.delta_t = Param()#1.0/4.0;  #time coefficient represents the 15 minutesin hour

model.demand = Param(model.RH, mutable = True, within = NonNegativeReals)
model.pv = Param(model.RH, mutable = True, within = NonNegativeReals)
model.ev = Param(model.RH, mutable = True, within = Binary)

#Cost of Energy
model.c_buy = Param()#0.0002899; #euro/Wh
model.c_sell = Param()#0.00015; #euro/Wh


#Home Battery Control Constants
model.P_B_max = Param()#11.2e3 #W
model.P_B_min = Param()#3.7 #W
model.E_B_min = Param()#1.5e3 #W/h
model.E_B_max = Param()#8.8e3 #W/h
model.E_B_0 = Param()#5e3 #W/h
model.n_B_ch = Param()#0.9 #battery charging efficiency
model.n_B_dis = Param()#n_B_ch #battery discharging efficiency

#Battery Optimization Variables
model.P_B_ch = Var(model.RH, within = NonNegativeReals)
model.P_B_dis = Var(model.RH, within = NonNegativeReals)
model.y = Var(model.RH, within = Binary)
model.z = Var(model.RH, within = Binary)

#Battery Energy Value


#SOC calculation for Battery
def E_B_calc(model, i):
    #for counter in range(0, 24): 
        if i == 0: 
            return model.E_B_0 + (model.P_B_ch[i]*model.n_B_ch*model.delta_t) - (model.P_B_dis[i] * model.delta_t/model.n_B_dis)
        else:
           return model.E_B_exp[i-1] + (model.P_B_ch[i]*model.n_B_ch*model.delta_t) - (model.P_B_dis[i] * model.delta_t/model.n_B_dis)
    
#EV(BMW i3) Battery Control Constants #https://www.bmw.com.tr/tr/all-models/bmw-i/i3/2017/range-charging-efficiency.html
model.P_EV_max = Param()#11e3 #Allowed ppower output of charger W
model.P_EV_min = Param()#11e3 #Allowed ppower output of charger W
model.E_EV_min = Param()#6e3 #https://ev-database.uk/car/1104/BMW-i3 W
model.E_EV_max = Param()#33e3 #W/h
model.E_EV_0 = Param()#15e3 #W/h
model.n_EV_ch = Param()#0.9 #EV charge efficiency
model.n_EV_dis = Param()#n_EV_ch #EV discharge efficiency
model.n_EV_drive = Param()#0.7 #EV drive efficiency
model.E_EV_goal = Param()#26.4e3 #EV goal energy value W/h
model.P_EV_drive = Param()#1.2e3 #https://www.holmgrensbil.se/globalassets/nya-bilar/bmw/modellsidor/i3/dokument/i3-psl-eal_web.pdf
model.SOC_EV_goal = Param()#0.8 #Goal SOC in percentage

#EV Optimization Variables
model.P_EV_ch = Var(model.RH, within = NonNegativeReals)
model.P_EV_dis = Var(model.RH, within = NonNegativeReals)
model.w = Var(model.RH, within = Binary)
model.x = Var(model.RH, within = Binary)

#EV Energy Value


#E_EV level calculator
def E_EV_calc(model, i):
    #for counter in range(0, 24):
        if i == 0:
            if model.ev[i] == 1:
                q = 1
                m = 0
            else: 
                q = 0
                m = 1
                model.w[i] = 0
                model.x[i] = 0
            return model.E_EV_0 + q*(model.P_EV_ch[i]*model.n_EV_ch*model.delta_t - model.P_EV_dis[i] * model.delta_t/model.n_EV_dis) -m*((model.P_EV_drive/model.n_EV_drive)*model.delta_t)
        else:
            if model.ev[i] == 1:
                q = 1
                m = 0
            else:
                q = 0
                m = 1
                model.w[i] = 0
                model.x[i] = 0
            return model.E_EV_exp[i-1] + q*(model.P_EV_ch[i]*model.n_EV_ch*model.delta_t - model.P_EV_dis[i] * model.delta_t/model.n_EV_dis) -m*((model.P_EV_drive/model.n_EV_drive)*model.delta_t)

   

#Grid Constants
model.P_grid_max = Param()#33000.0 #W
model.P_inject_max = Param()#33000.0 #W

#Grid Optimization Variables
model.P_grid = Var(model.RH, within = NonNegativeReals)
model.P_inject = Var(model.RH, within = NonNegativeReals)


#model.E_B_exp = Expression(model.RH, rule=E_B_calc)
model.E_B_exp = Expression(model.RH, rule=E_B_calc)
model.E_EV_exp = Expression(model.RH, rule=E_EV_calc)

#   Battery Constraints
model.Battery_cons1 = Constraint(model.RH, rule = lambda model,  j: 0 <= model.y[j] + model.z[j] <= 1) #Preventing the charge and discharge of battery at the same time
model.Battery_cons2 = Constraint(model.RH, rule = lambda model,  j:  model.P_B_ch[j] <= model.P_B_max*model.y[j]) #Maximum charge power constraint
model.Battery_cons3 = Constraint(model.RH, rule = lambda model,  j:  model.P_B_dis[j] <= model.P_B_max*model.z[j]) #Maximum discharge power constraint
model.Battery_cons4 = Constraint(model.RH, rule = lambda model,  j: model.E_B_min <= model.E_B_exp[j] <= model.E_B_max) #Battery energy level constraint 
#   EV Constraints
model.EV_cons1 = Constraint(model.RH, rule = lambda model,  j: 0 <= model.w[j] + model.x[j] <= 1) #Preventing the charge and discharge of EV at the same time
model.EV_cons2 = Constraint(model.RH, rule = lambda model,  j:  model.P_EV_ch[j] <= model.P_EV_max*model.w[j]) #Maximum charge power constraint
model.EV_cons3 = Constraint(model.RH, rule = lambda model,  j:  model.P_EV_dis[j] <= model.P_EV_max*model.x[j]) #Maximum discharge power constraint
model.EV_cons4 = Constraint(model.RH, rule = lambda model,  j: model.E_EV_min <= model.E_EV_exp[j] <= model.E_EV_max) #Battery energy level constraint

def chargeRule(model, j):
    if model.ev[j] == 0:
        return model.P_EV_ch[j] ==0
    else:
        return Constraint.Skip
   
model.EV_cons5 = Constraint(model.RH, rule = chargeRule)

def dischargeRule(model, j):
    if model.ev[j] == 0:
        return model.P_EV_dis[j] == 0
    else:
        return Constraint.Skip

model.EV_cons6 = Constraint(model.RH, rule = dischargeRule)   



if v2h_selection == 'no_v2h':
    model.EV_cons8 = Constraint(model.RH, rule = lambda model, j: model.P_EV_dis[j] == 0)
else: 
    Constraint.Skip
  
#   Grid Constraints  
model.Grid_cons1 = Constraint(model.RH, rule = lambda model, j: 0.0 <= model.P_grid[j] <= model.P_grid_max)
model.Grid_cons2 = Constraint(model.RH, rule = lambda model, j: 0.0 <= model.P_inject[j] <= model.P_inject_max)

#   Power Balance
if v2h_selection == 'no_v2h':
    model.Balance_cons1 = Constraint(model.RH, rule = lambda model, j: model.demand[j] + model.P_B_ch[j] + model.P_EV_ch[j] - model.P_grid[j] - model.pv[j] - model.P_B_dis[j] + model.P_inject[j]==0.0)
else:
    model.Balance_cons1 = Constraint(model.RH, rule = lambda model, j: model.demand[j] + model.P_B_ch[j] + model.P_EV_ch[j] - model.P_grid[j] - model.pv[j] - model.P_B_dis[j] - model.P_EV_dis[j] + model.P_inject[j]==0.0)


def ComputeFirstStageCost_rule(model):
    return model.P_grid[0]*model.c_buy*model.delta_t
model.FirstStageCost = Expression( rule=ComputeFirstStageCost_rule)

def ComputeSecondStageCost_rule(model):
    return sum( model.P_grid[i]*model.c_buy*model.delta_t for i in model.RH)
model.SecondStageCost = Expression( rule=ComputeSecondStageCost_rule)

  
#StageSet = RangeSet(2)
#def cost_rule(m, stage):
#    # Just assign the expressions to the right stage
#    if stage == 1:
#        return model.FirstStageCost
#    if stage == 2:
#        return model.SecondStageCost
#model.CostExpressions = Expression(StageSet, rule=cost_rule)

def total_cost_rule(model):
    return model.SecondStageCost
model.TotalCostObjective = Objective( rule = total_cost_rule, sense = minimize)
    
