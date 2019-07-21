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
model = ConcreteModel()

#Reading the input data
availability_data = pandas.read_excel('ev.xlsx')
pv_data = pandas.read_excel('pv.xlsx')
demand_data = pandas.read_excel('ph.xlsx')
c_buy_data = pandas.read_excel('c_buy.xlsx')
c_sell_data = pandas.read_excel('c_sell.xlsx')
pricing = "Variable"

#####################Objective Function Selection#####################################
"""                                                                                  # 
    The objective function must be entered depending on user choice                  #
                                                                                     #
    							                             #
                                                                                     #
    									             #
                                					             #
                                                                                     #
                                                                                     #
    Secondly, desired the objective must be defined.                                 #
    objective_function = 'energy'               #for energy usage optimization       #
                         'cost'                 #for energy cost optimization        #
                         'income'               #for income optimization             #
                         
                         'self_consumption'     #for increasing the self comsumption #
                          self_consumption stops at 123 no_v2h 158                   # 
                                                                                     #                          
    v2h_selection =      'no_v2h'               #for no vehicle to home              #
                         'v2h'                  #for enablingthe vehicle to home     #
"""                                                                                  #
                                                   #
v2h_selection = 'v2h'                                                                #
objective_function = 'income'                                              #
######################################################################################

#Get the input values
availability_full = availability_data['ev'].values
P_pv_full = pv_data['pv'].values*1000
P_demand_full = demand_data['ph'].values*1000
global constraint_starter
global vehicle_charge_deadline
constraint_starter = []

#time step is 15 minutes
ndays = 365
one_week = 96*7
nperiods = 96*ndays#96*ndays
shift = 0
nsteps = 432
T_overlap = 48 #48
T_step = 81 #81
T_rh = T_overlap + T_step
step_finalizer = T_rh
shift = 0
shift_week = 0
delta_t = 1.0/4.0;  #time coefficient represents the 15 minutesin hour

#Solution Matrices
E_B_sol = numpy.zeros((nperiods), dtype = float) #Battery energy level
E_EV_sol = numpy.zeros((nperiods), dtype = float) #EV energy level
SOC_B_sol = numpy.zeros((nperiods), dtype = float) #SOC Battery
SOC_EV_sol = numpy.zeros((nperiods), dtype = float) #SOC EV
P_B_ch_sol = numpy.zeros((nperiods), dtype = float) #Battery charge power
P_B_dis_sol = numpy.zeros((nperiods), dtype = float) #Battery discharge power
P_EV_ch_sol = numpy.zeros((nperiods), dtype = float) #EV charge power
P_EV_dis_sol = numpy.zeros((nperiods), dtype = float) #EV discharge power 
P_grid_sol = numpy.zeros((nperiods), dtype = float) #Power drawn fromthe grid
P_inject_sol = numpy.zeros((nperiods), dtype = float) #Powerinjected to grid
y_sol = numpy.zeros((nperiods), dtype = int) #Battery charge controller
z_sol = numpy.zeros((nperiods), dtype = int) #Battery discharge controller
w_sol = numpy.zeros((nperiods), dtype = int) #EV charge controller
x_sol = numpy.zeros((nperiods), dtype = int) #EV discharge controller
User_Convenience_sol = numpy.zeros((nperiods), dtype = float) #Battery energy level
solution = numpy.empty((nperiods), dtype = object)
availability_difference_sol = numpy.zeros((nperiods), dtype = int)

rolling_horizon_range = range(T_rh)
model.RH = Set(initialize=rolling_horizon_range, ordered = True) # Modelset initialization

#Cost of Energy
if pricing == "Constant":
    c_buy = 0.0002899; #euro/Wh
    c_sell = 0.00015; #euro/Wh
else:
    c_buy_full = c_buy_data['c_buy'].values
    c_sell_full = c_sell_data['c_sell'].values

#Home Battery Control Constants
P_B_max = 11.2e3 #W
P_B_min = 3.7 #W
E_B_min = 1.5e3 #W/h
E_B_max = 8.8e3 #W/h
E_B_0 = 5e3 #W/h
n_B_ch = 0.9 #battery charging efficiency
n_B_dis = n_B_ch #battery discharging efficiency

#Battery Optimization Variables
model.P_B_ch = Var(model.RH, within = NonNegativeReals)
model.P_B_dis = Var(model.RH, within = NonNegativeReals)
model.y = Var(model.RH, within = Binary)
model.z = Var(model.RH, within = Binary)

#Battery Energy Value
model.E_B = Expression(model.RH)

#SOC calculation for Battery
def E_B_calc(rng, iteration_number, E_B_initial):
    for counter in range(0, rng): 
        if iteration_number<1:
            if counter == 0: 
                model.E_B[counter] = E_B_initial + (model.P_B_ch[counter]*n_B_ch*delta_t) - (model.P_B_dis[counter] * delta_t/n_B_dis)
            else:
                model.E_B[counter] = model.E_B[counter-1] + (model.P_B_ch[counter]*n_B_ch*delta_t) - (model.P_B_dis[counter] * delta_t/n_B_dis)
        elif iteration_number>=1:
            E_B_initial = value(model.E_B[T_step-1])
            if counter==0:
                model.E_B[counter] = E_B_initial + (model.P_B_ch[counter]*n_B_ch*delta_t) - (model.P_B_dis[counter] * delta_t/n_B_dis)
            elif counter>0:
                model.E_B[counter] = model.E_B[counter-1] + (model.P_B_ch[counter]*n_B_ch*delta_t) - (model.P_B_dis[counter] * delta_t/n_B_dis)
    return model.E_B
    
#EV(BMW i3) Battery Control Constants #https://www.bmw.com.tr/tr/all-models/bmw-i/i3/2017/range-charging-efficiency.html
P_EV_max = 11e3 #Allowed ppower output of charger W
E_EV_min = 6e3 #https://ev-database.uk/car/1104/BMW-i3 W
E_EV_max = 33e3 #W/h
E_EV_0 = 15e3 #W/h
n_EV_ch = 0.9 #EV charge efficiency
n_EV_dis = n_EV_ch #EV discharge efficiency
n_EV_drive = 0.7 #EV drive efficiency
E_EV_goal = 26.4e3 #EV goal energy value W/h
P_EV_drive = 1.2e3 #https://www.holmgrensbil.se/globalassets/nya-bilar/bmw/modellsidor/i3/dokument/i3-psl-eal_web.pdf
SOC_EV_goal = 0.8 #Goal SOC in percentage

#EV Optimization Variables
model.P_EV_ch = Var(model.RH, within = NonNegativeReals)
model.P_EV_dis = Var(model.RH, within = NonNegativeReals)
model.w = Var(model.RH, within = Binary)
model.x = Var(model.RH, within = Binary)

#EV Energy Value
model.E_EV = Expression(model.RH)

#E_EV level calculator
def E_EV_calc(rng, iteration_number, av_data, E_EV_initial):
    for counter in range(0, rng):
        if iteration_number < 1:
            if counter == 0:
                if av_data[counter] == 1:
                    q = 1
                    m = 0
                else: 
                    q = 0
                    m = 1
                    model.w[counter] = 0
                    model.x[counter] = 0
                model.E_EV[0] = E_EV_initial + q*(model.P_EV_ch[0]*n_EV_ch*delta_t - model.P_EV_dis[0] * delta_t/n_EV_dis) -m*((P_EV_drive/n_EV_drive)*delta_t)
            else:
                if av_data[counter] == 1:
                    q = 1
                    m = 0
                else:
                    q = 0
                    m = 1
                    model.w[counter] = 0
                    model.x[counter] = 0
                model.E_EV[counter] = model.E_EV[counter-1] + q*(model.P_EV_ch[counter]*n_EV_ch*delta_t - model.P_EV_dis[counter] * delta_t/n_EV_dis) -m*((P_EV_drive/n_EV_drive)*delta_t)
        elif iteration_number >= 1:
            E_EV_initial = value(model.E_EV[T_step-1])
            if counter == 0:
                if av_data[counter] == 1:
                    q = 1
                    m = 0
                else: 
                    q = 0
                    m = 1
                    model.w[counter] = 0
                    model.x[counter] = 0
                model.E_EV[0] = E_EV_initial + q*(model.P_EV_ch[0]*n_EV_ch*delta_t - model.P_EV_dis[0] * delta_t/n_EV_dis) -m*((P_EV_drive/n_EV_drive)*delta_t)
            else:
                if av_data[counter] == 1:
                    q = 1
                    m = 0
                else:
                    q = 0
                    m = 1
                    model.w[counter] = 0
                    model.x[counter] = 0
                model.E_EV[counter] = model.E_EV[counter-1] + q*(model.P_EV_ch[counter]*n_EV_ch*delta_t - model.P_EV_dis[counter] * delta_t/n_EV_dis) -m*((P_EV_drive/n_EV_drive)*delta_t)
    return model.E_EV

#Grid Constants
P_grid_max = 33000.0 #W
P_inject_max = 33000.0 #W

#Grid Optimization Variables
model.P_grid = Var(model.RH, within = NonNegativeReals)
model.P_inject = Var(model.RH, within = NonNegativeReals)
#model.P_grid_multiplier = Var(model.RH, within = Binary)
#model.P_inject_multiplier = Var(model.RH, within = Binary)

#User Convenıence Model
deadline = 0;
model.SOC_EV = Expression(model.RH)
model.Min_Slots = Expression(model.RH)
min_slots = numpy.empty((T_rh), dtype = object)
model.User_Convenience = Expression(model.RH)
user_convenience_level = numpy.ones(T_rh, dtype = object)

#The function that returns the departure slot of the EV
def difference(list_name):
    return [x - list_name[i - 1] for i, x in enumerate(list_name)][1:]

#UserConvenience Model
def User_Convenience_calc(stop):
    global constraint_starter
    global vehicle_charge_deadline
    vehicle_charge_deadline = 0
    constraint_starter = numpy.zeros((129), dtype = int)
    vehicle_charge_deadline = 0
    vehicle_charge_start = 0
    for counter in range(0,stop):
        model.User_Convenience[counter] = 0.1

    availability_difference = difference(availability)
    for counter in range(0, T_rh-1):
        if availability_difference[counter] == -1:
            vehicle_charge_deadline = counter
            for counter_2 in range(0, counter):
                if availability_difference[counter_2] == 1:
                    vehicle_charge_start = counter_2
                else:
                    vehicle_charge_start = 0
            break
    if vehicle_charge_deadline > 0:
        for counter in range(vehicle_charge_start, vehicle_charge_deadline+1):
            constraint_starter[counter] = 1
            min_slots[counter] = (E_EV_goal - model.E_EV[counter])/P_EV_max
            user_convenience_level[counter] = (vehicle_charge_deadline * delta_t - counter * delta_t + 1)
#            if user_convenience_level[counter] <= 0:
#                user_convenience_level[counter] = 1
            model.User_Convenience[counter] = min_slots[counter] / user_convenience_level[counter]
        
        for counter in range(vehicle_charge_deadline+1, len(model.RH)):
            model.User_Convenience[counter] = 0.1

    return model.User_Convenience

#main loop
for rh in range(0, nsteps):
    availability = availability_full[0+shift:T_rh+shift]
    availability_difference =  difference(availability_full[0+shift:128+shift])
    P_pv = P_pv_full[0+shift:T_rh+shift]
    P_demand = P_demand_full[0+shift:T_rh+shift]
    if pricing == "Variable":
        c_buy = c_buy_full[0+shift:T_rh+shift]
        c_sell = c_sell_full[0+shift:T_rh+shift]
    
    E_B_exp = E_B_calc(T_rh, rh, E_B_0)
    E_EV_exp = E_EV_calc(T_rh, rh, availability, E_EV_0)
    User_Convenience_exp = User_Convenience_calc(T_rh)

#   Battery Constraints
    model.Battery_cons1 = Constraint(model.RH, rule = lambda model,  j: 0 <= model.y[j] + model.z[j] <= 1) #Preventing the charge and discharge of battery at the same time
    model.Battery_cons2 = Constraint(model.RH, rule = lambda model,  j:  model.P_B_ch[j] <= P_B_max*model.y[j]) #Maximum charge power constraint
    model.Battery_cons3 = Constraint(model.RH, rule = lambda model,  j:  model.P_B_dis[j] <= P_B_max*model.z[j]) #Maximum discharge power constraint
    model.Battery_cons4 = Constraint(model.RH, rule = lambda model,  j: E_B_min <= E_B_exp[j] <= E_B_max) #Battery energy level constraint 
#   EV Constraints
    model.EV_cons1 = Constraint(model.RH, rule = lambda model,  j: 0 <= model.w[j] + model.x[j] <= 1) #Preventing the charge and discharge of EV at the same time
    model.EV_cons2 = Constraint(model.RH, rule = lambda model,  j:  model.P_EV_ch[j] <= P_EV_max*model.w[j]) #Maximum charge power constraint
    model.EV_cons3 = Constraint(model.RH, rule = lambda model,  j:  model.P_EV_dis[j] <= P_EV_max*model.x[j]) #Maximum discharge power constraint
    model.EV_cons4 = Constraint(model.RH, rule = lambda model,  j: E_EV_min <= E_EV_exp[j] <= E_EV_max) #Battery energy level constraint
    
    def chargeRule(model, j):
        if availability[j] == 0:
            return model.P_EV_ch[j] ==0
        else:
            return Constraint.Skip
       
    model.EV_cons5 = Constraint(model.RH, rule = chargeRule)
    
    def dischargeRule(model, j):
        if availability[j] == 0:
            return model.P_EV_dis[j] == 0
        else:
            return Constraint.Skip

    model.EV_cons6 = Constraint(model.RH, rule = dischargeRule)   

    def minSlotsRule(model, j):
        if constraint_starter[j] ==  1:
            return model.E_EV[vehicle_charge_deadline] >= E_EV_goal
        else:
            return Constraint.Skip
        
    model.EV_cons7 = Constraint(model.RH, rule = minSlotsRule)
    
    if v2h_selection == 'no_v2h':
        model.EV_cons8 = Constraint(model.RH, rule = lambda model, j: model.P_EV_dis[j] == 0)
    else: 
        Constraint.Skip
      
#   Grid Constraints  
    model.Grid_cons1 = Constraint(model.RH, rule = lambda model, j: 0.0 <= model.P_grid[j] <= P_grid_max)
    model.Grid_cons2 = Constraint(model.RH, rule = lambda model, j: 0.0 <= model.P_inject[j] <= P_inject_max)

#   Power Balance
    if v2h_selection == 'no_v2h':
        model.Balance_cons1 = Constraint(model.RH, rule = lambda model, j: P_demand[j] + model.P_B_ch[j] + model.P_EV_ch[j] - model.P_grid[j] - P_pv[j] - model.P_B_dis[j] + model.P_inject[j]==0)
    else:
        model.Balance_cons1 = Constraint(model.RH, rule = lambda model, j: P_demand[j] + model.P_B_ch[j] + model.P_EV_ch[j] - model.P_grid[j] - P_pv[j] - model.P_B_dis[j] - model.P_EV_dis[j] + model.P_inject[j]==0)

#   Objective Functions
#    if objective_function == 'energy':
#        model.energy = Objective(expr = sum(0.99*(model.P_B_ch[j]*delta_t - model.P_B_dis[j]*delta_t +model.P_EV_ch[j]*delta_t - model.P_EV_dis[j]*delta_t)  + 0.01*User_Convenience_exp[j]  for j in model.RH), sense = minimize)
    if objective_function == 'energy':
        model.energy = Objective(expr = sum((model.P_inject[j]*delta_t + P_demand[j]*delta_t + model.P_EV_ch[j]*delta_t + model.P_B_ch[j]*delta_t)  + User_Convenience_exp[j]  for j in model.RH), sense = minimize)
    elif objective_function == 'cost':
        model.cost = Objective(expr = sum(model.P_grid[j]*c_buy[j]*delta_t + User_Convenience_exp[j]  for j in model.RH), sense = minimize)
    elif objective_function == 'cost_2':
        model.cost = Objective(expr = sum(model.P_grid[j]*delta_t + User_Convenience_exp[j]  for j in model.RH), sense = minimize)
    elif objective_function == 'income':
        model.income = Objective(expr = sum(model.P_grid[j]*c_buy[j]*delta_t-model.P_inject[j]*c_sell[j]*delta_t + User_Convenience_exp[j]  for j in model.RH), sense = minimize)
    elif objective_function == 'income_3':
        model.income = Objective(expr = sum(model.P_grid[j]*delta_t-model.P_inject[j]*delta_t + User_Convenience_exp[j]  for j in model.RH), sense = minimize)
    elif objective_function == 'income_2':
        model.income = Objective(expr = sum(model.P_inject[j]*c_sell[j]*delta_t + User_Convenience_exp[j]  for j in model.RH), sense = maximize)
#    elif objective_function == 'no_v2h':
#        model.no_v2h = Objective(expr = sum(-model.P_grid[j]*c_buy[j]*delta_t + User_Convenience_exp[j]  for j in model.RH), sense = minimize)    
    elif objective_function == 'self_consumption':
        model.self_consumption = Objective(expr = sum((model.P_grid[j] + model.P_inject[j])*delta_t + User_Convenience_exp[j]  for j in model.RH), sense = minimize)
    else: 
        print("An undefined objective request entered! Please check your choice")
    
    
    solver = SolverFactory("gurobi")

    #solution[0+shift:T_rh+shift] = solver.solve(model)
    solver.solve(model)



#Solution Matrices are stored here    
    for i in model.RH:
        E_B_sol[i+shift] = value(model.E_B[i])
        E_EV_sol[i+shift] = value(model.E_EV[i])
        SOC_B_sol[i+shift] = value(model.E_B[i])/E_B_max
        SOC_EV_sol[i+shift] = value(model.E_EV[i])/E_EV_max
        P_B_ch_sol[i+shift] = value(model.P_B_ch[i])
        P_B_dis_sol[i+shift] = value(model.P_B_dis[i])
        P_EV_ch_sol[i+shift] = value(model.P_EV_ch[i])
        P_EV_dis_sol[i+shift] = value(model.P_EV_dis[i])
        P_grid_sol[i+shift] = value(model.P_grid[i])
        P_inject_sol[i+shift] = value(model.P_inject[i])
        y_sol[i+shift] = value(model.y[i])
        z_sol[i+shift] = value(model.z[i])
        w_sol[i+shift] = value(model.w[i])
        x_sol[i+shift] = value(model.x[i])
        User_Convenience_sol[i+shift] = value(model.User_Convenience[i])
    for i in range(0, 127):
        availability_difference_sol[i+shift] = availability_difference[i]
    
    shift = shift+T_step
    print(rh)
    print(shift)
  
#Total Results
energy_grid = sum(P_grid_sol)*delta_t/1000
energy_inject = sum(P_inject_sol)*delta_t/1000
total_EV_charge = sum(P_EV_ch_sol)*delta_t/1000
total_EV_discharge = sum(P_EV_dis_sol)*delta_t/1000
total_B_charge = sum(P_B_ch_sol)*delta_t/1000
total_B_discharge = sum(P_B_dis_sol)*delta_t/1000
total_EV_drive = sum(availability_full)*P_EV_drive*delta_t/1000
maximum_energy_grid = max(P_grid_sol)*delta_t/1000
maximum_energy_inject = max(P_inject_sol)*delta_t/1000
maximum_SOC_Battery = max(SOC_B_sol)*100
minimum_SOC_Battery = min(SOC_B_sol)*100
maximum_SOC_EV = max(SOC_EV_sol)*100
minimum_SOC_EV = min(SOC_EV_sol)*100
total_cost_energy = sum(numpy.multiply(P_grid_sol, c_buy_full))*delta_t
total_income_energy = sum(numpy.multiply(P_inject_sol,c_sell_full))*delta_t
total_profit_energy = (-sum(numpy.multiply(P_grid_sol, c_buy_full))*delta_t + sum(numpy.multiply(P_inject_sol,c_sell_full))*delta_t)

#Data Visualition
width = 0.5 #line width for the plots
data_range =500 #the data rangeof plots

start = dt.datetime(2018, 1, 1, 0, 0) #Starting time is accepted as 01.January.2018
time = [start + dt.timedelta(minutes = j*15) for j in range(len(E_B_sol))]    

#Saving directory creation for figures    
#if os.path.isdir('/media/mert/My Passport/optimization_figures/Figures/MILP_'+objective_function) == False:
#    os.mkdir('/media/mert/My Passport/optimization_figures/Figures/MILP_'+objective_function)
if os.path.isdir('/media/mert/D02A-A409/Figures/MILP/'+objective_function+'_'+v2h_selection+'_'+pricing+'_Pricing_'+str(ndays)+'_days_'+str(T_rh)+'_RH_size') == False:
    os.mkdir('/media/mert/D02A-A409/Figures/MILP/'+objective_function+'_'+v2h_selection+'_'+pricing+'_Pricing_'+str(ndays)+'_days_'+str(T_rh)+'_RH_size')
    destination = '/media/mert/D02A-A409/Figures/MILP/'+objective_function+'_'+v2h_selection+'_'+pricing+'_Pricing_'+str(ndays)+'_days_'+str(T_rh)+'_RH_size'
else:
    destination = '/media/mert/D02A-A409/Figures/MILP/'+objective_function+'_'+v2h_selection+'_'+pricing+'_Pricing_'+str(ndays)+'_days_'+str(T_rh)+'_RH_size'
    
#Numerical Value File Creation
file_name = "total_results_"+v2h_selection+'_'+pricing+"_"+objective_function
complete_name = os.path.join(destination, file_name+".txt")
file = open(complete_name, "w+")
file.write("##########RESULTS##########\r\n")
file.write("Total energy drawn from grid = %f kWh\r\n" %energy_grid)
file.write("Total energy inject to grid = %f kWh\r\n" %energy_inject)
file.write("Total energy used for charging EV = %f kWh\r\n" %total_EV_charge)
file.write("Total energy used for discharging EV = %f kWh\r\n" %total_EV_discharge)
file.write("Total energy used EV for driving = %f kWh\r\n" %total_EV_drive)
file.write("Total energy used for charging Battery = %f kWh\r\n" %total_B_charge)
file.write("Total energy used for discharging Battery = %f kWh\r\n" %total_B_discharge)
file.write("Maximum energy drawn from grid = %f kWh\r\n" %maximum_energy_grid)
file.write("Maximum energy inject to grid = %f kWh\r\n" %maximum_energy_inject)
file.write("Maximum SOC of Battery = %f\r\n" %maximum_SOC_Battery)
file.write("Minimum SOC of Battery = %f\r\n" %minimum_SOC_Battery)
file.write("Maximum SOC of EV = %f \r\n" %maximum_SOC_EV)
file.write("Minimum SOC of EV = %f \r\n" %minimum_SOC_EV)
file.write("Total energy cost = %f €\r\n" %total_cost_energy)
file.write("Total energy income = %f €\r\n" %total_income_energy)
file.write("Total profit = %f €\r\n" %total_profit_energy)
file.write("#######################################")
file.close()            

#Storing the excel files
#P_B_ch_sol
workbook1 = xlsxwriter.Workbook(destination+'/P_B_ch_sol_'+v2h_selection+'_'+pricing+'_'+objective_function+'.xlsx')
worksheet1 = workbook1.add_worksheet()
row = 0
column = 0
for item in P_B_ch_sol:
    worksheet1.write(row, column, item)
    row += 1
workbook1.close()

#P_B_dis_sol
workbook2 = xlsxwriter.Workbook(destination+'/P_B_dis_sol'+v2h_selection+'_'+pricing+'_'+objective_function+'.xlsx')
worksheet2 = workbook2.add_worksheet()
row = 0
column = 0
for item in P_B_dis_sol:
    worksheet2.write(row, column, item)
    row += 1
workbook2.close()

#P_EV_ch_sol
workbook3 = xlsxwriter.Workbook(destination+'/P_EV_ch_sol'+v2h_selection+'_'+pricing+'_'+objective_function+'.xlsx')
worksheet3 = workbook3.add_worksheet()
row = 0
column = 0
for item in P_EV_ch_sol:
    worksheet3.write(row, column, item)
    row += 1
workbook3.close()

#P_EV_dis_sol
workbook4 = xlsxwriter.Workbook(destination+'/P_EV_dis_sol'+v2h_selection+'_'+pricing+'_'+objective_function+'.xlsx')
worksheet4 = workbook4.add_worksheet()
row = 0
column = 0
for item in P_EV_dis_sol:
    worksheet4.write(row, column, item)
    row += 1
workbook4.close()

#P_grid_sol
workbook5 = xlsxwriter.Workbook(destination+'/P_grid_sol'+v2h_selection+'_'+pricing+'_'+objective_function+'.xlsx')
worksheet5 = workbook5.add_worksheet()
row = 0
column = 0
for item in P_grid_sol:
    worksheet5.write(row, column, item)
    row += 1
workbook5.close()

#P_inject_sol
workbook6 = xlsxwriter.Workbook(destination+'/P_inject_sol'+v2h_selection+'_'+pricing+'_'+objective_function+'.xlsx')
worksheet6 = workbook6.add_worksheet()
row = 0
column = 0
for item in P_inject_sol:
    worksheet6.write(row, column, item)
    row += 1
workbook6.close()

#E_B_sol
workbook7 = xlsxwriter.Workbook(destination+'/E_B_sol'+v2h_selection+'_'+pricing+'_'+objective_function+'.xlsx')
worksheet7 = workbook7.add_worksheet()
row = 0
column = 0
for item in E_B_sol:
    worksheet7.write(row, column, item)
    row += 1
workbook7.close()

#E_EV_sol
workbook8 = xlsxwriter.Workbook(destination+'/E_EV_sol'+v2h_selection+'_'+pricing+'_'+objective_function+'.xlsx')
worksheet8 = workbook8.add_worksheet()
row = 0
column = 0
for item in E_EV_sol:
    worksheet8.write(row, column, item)
    row += 1
workbook8.close()



for j in range(0, 52+1):
    
##E_B plot
#    fig_E_B = plt.figure(1)
#    plt.plot(time[0+shift_week:one_week+shift_week], E_B_sol[0+shift_week:one_week+shift_week], linewidth=width, label = 'Energy')
#    plt.gcf().autofmt_xdate()
#    plt.title('Battery Energy Level')
#    plt.legend()
#    plt.xlabel('Opt. Periods(15min)')
#    plt.ylabel('Energy(Wh)')
#    plt.savefig(destination + '/fig_E_B_'+str(j+1)+'_th_week.png', dpi=900)
#    plt.close()
############################################
#
##E_EV plot
#    fig_E_EV = plt.plot(time[0+shift_week:one_week+shift_week], E_EV_sol[0+shift_week:one_week+shift_week], linewidth=width, label = 'Energy')
#    plt.gcf().autofmt_xdate()
#    plt.title('EV Energy Level')
#    plt.legend()
#    plt.xlabel('Opt. Periods(15min)')
#    plt.ylabel('Energy(Wh)')
#    plt.savefig(destination + '/fig_E_EV_'+str(j+1)+'_th_week.png', dpi=900)
#    plt.close()
#############################################
#
##SOC_B plot
#    fig_SOC_B = plt.plot(time[0+shift_week:one_week+shift_week], SOC_B_sol[0+shift_week:one_week+shift_week]*100, linewidth=width, label = 'SOC')
#    plt.gcf().autofmt_xdate()
#    plt.title('Battery SOC')
#    plt.legend()
#    plt.xlabel('Opt. Periods(15min)')
#    plt.ylabel('SOC(%)')
#    plt.savefig(destination + '/fig_SOC_B_'+str(j+1)+'_th_week.png', dpi=900)
#    plt.close()
##############################################
#
##SOC_EV plot
#    fig_SOC_EV = plt.plot(time[0+shift_week:one_week+shift_week], SOC_EV_sol[0+shift_week:one_week+shift_week]*100, linewidth=width, label = 'SOC')
#    plt.gcf().autofmt_xdate()
#    plt.title('EV SOC')
#    plt.legend()
#    plt.xlabel('Opt. Periods(15min)')
#    plt.ylabel('SOC(%)')
#    plt.savefig(destination + '/fig_SOC_EV_'+str(j+1)+'_th_week.png', dpi=900)
#    plt.close()
###############################################
#
##P_B_ch plot
#    fig_P_B_ch = plt.plot(time[0+shift_week:one_week+shift_week], P_B_ch_sol[0+shift_week:one_week+shift_week], linewidth=width, label = 'Battery Power')
#    plt.gcf().autofmt_xdate()
#    plt.title('Battery Charge Power')
#    plt.legend()
#    plt.xlabel('Opt. Periods(15min)')
#    plt.ylabel('Power(W)')
#    plt.savefig(destination + '/fig_P_B_ch_'+str(j+1)+'_th_week.png', dpi=900)
#    plt.close()
###############################################
#
##P_B_dis plot
#    fig_P_B_dis = plt.plot(time[0+shift_week:one_week+shift_week], P_B_dis_sol[0+shift_week:one_week+shift_week], linewidth=width, label = 'Battery Power')
#    plt.gcf().autofmt_xdate()
#    plt.title('Battery Discharge Power')
#    plt.legend()
#    plt.xlabel('Opt. Periods(15min)')
#    plt.ylabel('Power(W)')
#    plt.savefig(destination + '/fig_P_B_dis_'+str(j+1)+'_th_week.png', dpi=900)
#    plt.close()
################################################
#
##P_EV_ch plot
#    fig_P_EV_ch = plt.plot(time[0+shift_week:one_week+shift_week], P_EV_ch_sol[0+shift_week:one_week+shift_week], linewidth=width, label = 'EV Power')
#    plt.gcf().autofmt_xdate()
#    plt.title('EV Charge Power')
#    plt.legend()
#    plt.xlabel('Opt. Periods(15min)')
#    plt.ylabel('Power(W)')
#    plt.savefig(destination + '/fig_P_EV_ch_'+str(j+1)+'_th_week.png', dpi=900)
#    plt.close()
################################################
#
##P_EV_dis plot
#    fig_P_EV_dis = plt.plot(time[0+shift_week:one_week+shift_week], P_EV_dis_sol[0+shift_week:one_week+shift_week], linewidth=width, label = 'EV Power')
#    plt.gcf().autofmt_xdate()
#    plt.title('EV Discharge Power')
#    plt.legend()
#    plt.xlabel('Opt. Periods(15min)')
#    plt.ylabel('Power(W)')
#    plt.savefig(destination + '/fig_P_EV_dis_'+str(j+1)+'_th_week.png', dpi=900)
#    plt.close()
#################################################
#
##User Convenience
#    fig_User_Convenience = plt.plot(time[0+shift_week:one_week+shift_week], User_Convenience_sol[0+shift_week:one_week+shift_week], linewidth=width, label = 'User Convenience')
#    plt.gcf().autofmt_xdate()
#    plt.title('User Convenience')
#    plt.legend()
#    plt.xlabel('Opt. Periods(15min)')
#    plt.ylabel('Percentage')
#    plt.savefig(destination + '/fig_User_Convenience_'+str(j+1)+'_th_week.png', dpi=900)
#    plt.close()
#####################################################################
    

#Creative and Defining Figures
    fig_P_EV_check = plt.plot(time[0+shift_week:one_week+shift_week], P_EV_ch_sol[0+shift_week:one_week+shift_week] - P_EV_dis_sol[0+shift_week:one_week+shift_week], linewidth=width, label = 'EV Power')
    fig_EV_availability = plt.plot(time[0+shift_week:one_week+shift_week], availability_full[0+shift_week:one_week+shift_week]*10000, linewidth=width, label = 'EV availability')
    plt.gcf().autofmt_xdate()
    plt.title('EV Check for ' + objective_function)
    plt.legend()
    plt.xlabel('Opt. Periods(15min)')
    plt.ylabel('Power(W)')
    plt.tight_layout()
    plt.savefig(destination + '/fig_EV_check_'+str(j+1)+'_th_week.png', dpi=900)
    plt.close()
    
#EV charge and the Electricity Cost
    fig_P_EV_check = plt.plot(time[0+shift_week:one_week+shift_week], P_EV_ch_sol[0+shift_week:one_week+shift_week] - P_EV_dis_sol[0+shift_week:one_week+shift_week], linewidth=width, label = 'EV Power')
    fig_cost_buy = plt.plot(time[0+shift_week:one_week+shift_week], c_buy_full[0+shift_week:one_week+shift_week]*100000000, linewidth=width, label = 'Buy Price')
    fig_cost_sell = plt.plot(time[0+shift_week:one_week+shift_week], c_sell_full[0+shift_week:one_week+shift_week]*100000000, linewidth=width, label = 'Sell Price')
    plt.gcf().autofmt_xdate()
    plt.title('EV Charge variation depending on the electricity price ' + objective_function)
    plt.legend()
    plt.xlabel('Opt. Periods(15min)')
    plt.ylabel('Power(W)')
    plt.tight_layout()
    plt.savefig(destination + '/fig_EV_check_'+str(j+1)+'_th_week.png', dpi=900)
    plt.close()
#User Convenience check
    fig_User_Convenience_check = plt.plot(time[0+shift_week:one_week+shift_week], User_Convenience_sol[0+shift_week:one_week+shift_week]*100000, 'r--', label = 'User Convenience')
    fig_P_EV_check = plt.plot(time[0+shift_week:one_week+shift_week], P_EV_ch_sol[0+shift_week:one_week+shift_week] - P_EV_dis_sol[0+shift_week:one_week+shift_week], linewidth=width, label = 'EV Power')
    plt.gcf().autofmt_xdate()
    plt.title('User Convenience for '+ objective_function)
    plt.legend()
    plt.xlabel('Opt. Periods(15min)')
    plt.ylabel('Data')
    plt.tight_layout()
    plt.savefig(destination + '/fig_User_Convenience_check_'+str(j+1)+'_th_week.png', dpi=900)
    plt.close()

#House + PV
    fig_House = plt.plot(time[0+shift_week:one_week+shift_week], P_demand_full[0+shift_week:one_week+shift_week], linewidth=width, label = 'House')
    fig_PV = plt.plot(time[0+shift_week:one_week+shift_week], -P_pv_full[0+shift_week:one_week+shift_week], linewidth=width, label = 'PV')
    plt.gcf().autofmt_xdate()
    plt.title('House Demand and PV Generation for '+ objective_function)
    plt.legend()
    plt.xlabel('Opt. Periods(15min)')
    plt.ylabel('Power(W)')
    plt.tight_layout()
    plt.savefig(destination + '/fig_House_and_PV'+str(j+1)+'_th_week.png', dpi=900)
    plt.close()

#House + PV + Battery
    fig_House = plt.plot(time[0+shift_week:one_week+shift_week], P_demand_full[0+shift_week:one_week+shift_week], linewidth=width, label = 'House')
    fig_PV = plt.plot(time[0+shift_week:one_week+shift_week], -P_pv_full[0+shift_week:one_week+shift_week], linewidth=width, label = 'PV')
    fig_P_B = plt.plot(time[0+shift_week:one_week+shift_week], P_B_ch_sol[0+shift_week:one_week+shift_week] - P_B_dis_sol[0+shift_week:one_week+shift_week], linewidth=width, label = 'Battery')
    plt.gcf().autofmt_xdate()
    plt.title('House Demand, PV Generation and Battery Power for '+ objective_function)
    plt.legend()
    plt.xlabel('Opt. Periods(15min)')
    plt.ylabel('Power(W)')
    plt.tight_layout()
    plt.savefig(destination + '/fig_House_PV_and_Battery'+str(j+1)+'_th_week.png', dpi=900)
    plt.close()

#House + PV + EV
    fig_House = plt.plot(time[0+shift_week:one_week+shift_week], P_demand_full[0+shift_week:one_week+shift_week], linewidth=width, label = 'House')
    fig_PV = plt.plot(time[0+shift_week:one_week+shift_week], -P_pv_full[0+shift_week:one_week+shift_week], linewidth=width, label = 'PV')
    fig_P_EV = plt.plot(time[0+shift_week:one_week+shift_week], P_EV_ch_sol[0+shift_week:one_week+shift_week] - P_EV_dis_sol[0+shift_week:one_week+shift_week], linewidth=width, label = 'EV')
    plt.gcf().autofmt_xdate()
    plt.title('House Demand, PV Generation and EV Power for '+ objective_function)
    plt.legend()
    plt.xlabel('Opt. Periods(15min)')
    plt.ylabel('Power(W)')
    plt.tight_layout()
    plt.savefig(destination + '/fig_House_PV_and_EV'+str(j+1)+'_th_week.png', dpi=900)
    plt.close()

#Grid + Inject
    fig_P_grid = plt.plot(time[0+shift_week:one_week+shift_week], P_grid_sol[0+shift_week:one_week+shift_week], linewidth=width, label = 'Grid Power')
    fig_P_inject = plt.plot(time[0+shift_week:one_week+shift_week], -P_inject_sol[0+shift_week:one_week+shift_week], linewidth=width, label = 'Injected Power')
    fig_cost_buy = plt.plot(time[0+shift_week:one_week+shift_week], c_buy_full[0+shift_week:one_week+shift_week]*100000000, linewidth=width, label = 'Buy Price')
    fig_cost_sell = plt.plot(time[0+shift_week:one_week+shift_week], c_sell_full[0+shift_week:one_week+shift_week]*100000000, linewidth=width, label = 'Sell Price')
    plt.gcf().autofmt_xdate()
    plt.title('Grid and Inject Power variation depending on the price for '+ objective_function)
    plt.legend()
    plt.xlabel('Opt. Periods(15min)')
    plt.ylabel('Power(W)')
    plt.tight_layout()
    plt.savefig(destination + '/fig_P_grid_and_P_inject'+str(j+1)+'_th_week.png', dpi=900)
    plt.close()

#Savings
    fig_P_grid_price = plt.plot(time[0+shift_week:one_week+shift_week], -1*numpy.multiply(P_grid_sol[0+shift_week:one_week+shift_week], c_buy_full[0+shift_week:one_week+shift_week])*delta_t, linewidth=width, label = 'Cost')
    fig_P_inject_price = plt.plot(time[0+shift_week:one_week+shift_week], numpy.multiply(P_inject_sol[0+shift_week:one_week+shift_week], c_sell_full[0+shift_week:one_week+shift_week])*delta_t, linewidth=width, label = 'Earnings')
    #fig_price_difference = plt.plot(time[0+shift_week:one_week+shift_week], -P_grid_sol[0+shift_week:one_week+shift_week]*c_buy*delta_t + P_inject_sol[0+shift_week:one_week+shift_week]*c_sell*delta_t, 'r--', label = 'Profit')
    plt.gcf().autofmt_xdate()
    plt.title('Energy Cost and Earnings for '+ objective_function)
    plt.legend()
    plt.xlabel('Opt. Periods(15min)')
    plt.ylabel('Price(Euros)')
    plt.tight_layout()
    plt.savefig(destination + '/fig_Price'+str(j+1)+'_th_week.png', dpi=900)
    plt.close()    

    shift_week = shift_week + one_week


