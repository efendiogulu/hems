#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 19:43:20 2019

@author: mert
"""

#
#This script is written to convert the json results to excel files
#After the Stochastic Programming finish the Calculation Run this script to generate excel files
#

import csv
import json
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import os
import pandas
import numpy
import datetime as dt
from dateutil.relativedelta import *
from ReferenceModel import model #This command has to be run after the ReferenceModel.py is run
P_grid_portion = numpy.load('P_grid_portion.npy') 
P_inject_portion = numpy.load('P_inject_portion.npy') 
P_B_portion = numpy.load('P_B_portion.npy') 
P_EV_portion = numpy.load('P_EV_portion.npy')
P_demand_portion = numpy.load('P_demand_portion.npy') 

infile = open("results.json", "r")
infile_json = json.loads(infile.read())
print(infile_json[0])
total_scenarios = infile_json[1]
total_scenario10_content = total_scenarios['Scenario10Node']
total_scenario1_content = total_scenarios['Scenario1Node']
total_scenario2_content = total_scenarios['Scenario2Node']
total_scenario3_content = total_scenarios['Scenario3Node']
total_scenario4_content = total_scenarios['Scenario4Node']
total_scenario5_content = total_scenarios['Scenario5Node']
total_scenario6_content = total_scenarios['Scenario6Node']
total_scenario7_content = total_scenarios['Scenario7Node']
total_scenario8_content = total_scenarios['Scenario8Node']
total_scenario9_content = total_scenarios['Scenario9Node']

P_B_ch_sc_1 = total_scenario1_content['P_B_ch']
P_B_ch_sc_2 = total_scenario2_content['P_B_ch']
P_B_ch_sc_3 = total_scenario3_content['P_B_ch']
P_B_ch_sc_4 = total_scenario4_content['P_B_ch']
P_B_ch_sc_5 = total_scenario5_content['P_B_ch']
P_B_ch_sc_6 = total_scenario6_content['P_B_ch']
P_B_ch_sc_7 = total_scenario7_content['P_B_ch']
P_B_ch_sc_8 = total_scenario8_content['P_B_ch']
P_B_ch_sc_9 = total_scenario9_content['P_B_ch']
P_B_ch_sc_10 = total_scenario10_content['P_B_ch']

P_B_dis_sc_1 = total_scenario1_content['P_B_dis']
P_B_dis_sc_2 = total_scenario2_content['P_B_dis']
P_B_dis_sc_3 = total_scenario3_content['P_B_dis']
P_B_dis_sc_4 = total_scenario4_content['P_B_dis']
P_B_dis_sc_5 = total_scenario5_content['P_B_dis']
P_B_dis_sc_6 = total_scenario6_content['P_B_dis']
P_B_dis_sc_7 = total_scenario7_content['P_B_dis']
P_B_dis_sc_8 = total_scenario8_content['P_B_dis']
P_B_dis_sc_9 = total_scenario9_content['P_B_dis']
P_B_dis_sc_10 = total_scenario10_content['P_B_dis']

P_EV_ch_sc_1 = total_scenario1_content['P_EV_ch']
P_EV_ch_sc_2 = total_scenario2_content['P_EV_ch']
P_EV_ch_sc_3 = total_scenario3_content['P_EV_ch']
P_EV_ch_sc_4 = total_scenario4_content['P_EV_ch']
P_EV_ch_sc_5 = total_scenario5_content['P_EV_ch']
P_EV_ch_sc_6 = total_scenario6_content['P_EV_ch']
P_EV_ch_sc_7 = total_scenario7_content['P_EV_ch']
P_EV_ch_sc_8 = total_scenario8_content['P_EV_ch']
P_EV_ch_sc_9 = total_scenario9_content['P_EV_ch']
P_EV_ch_sc_10 = total_scenario10_content['P_EV_ch']

P_EV_dis_sc_1 = total_scenario1_content['P_EV_dis']
P_EV_dis_sc_2 = total_scenario2_content['P_EV_dis']
P_EV_dis_sc_3 = total_scenario3_content['P_EV_dis']
P_EV_dis_sc_4 = total_scenario4_content['P_EV_dis']
P_EV_dis_sc_5 = total_scenario5_content['P_EV_dis']
P_EV_dis_sc_6 = total_scenario6_content['P_EV_dis']
P_EV_dis_sc_7 = total_scenario7_content['P_EV_dis']
P_EV_dis_sc_8 = total_scenario8_content['P_EV_dis']
P_EV_dis_sc_9 = total_scenario9_content['P_EV_dis']
P_EV_dis_sc_10 = total_scenario10_content['P_EV_dis']

P_grid_sc_1 = total_scenario1_content['P_grid']
P_grid_sc_2 = total_scenario2_content['P_grid']
P_grid_sc_3 = total_scenario3_content['P_grid']
P_grid_sc_4 = total_scenario4_content['P_grid']
P_grid_sc_5 = total_scenario5_content['P_grid']
P_grid_sc_6 = total_scenario6_content['P_grid']
P_grid_sc_7 = total_scenario7_content['P_grid']
P_grid_sc_8 = total_scenario8_content['P_grid']
P_grid_sc_9 = total_scenario9_content['P_grid']
P_grid_sc_10 = total_scenario10_content['P_grid']

P_inject_sc_1 = total_scenario1_content['P_inject']
P_inject_sc_2 = total_scenario2_content['P_inject']
P_inject_sc_3 = total_scenario3_content['P_inject']
P_inject_sc_4 = total_scenario4_content['P_inject']
P_inject_sc_5 = total_scenario5_content['P_inject']
P_inject_sc_6 = total_scenario6_content['P_inject']
P_inject_sc_7 = total_scenario7_content['P_inject']
P_inject_sc_8 = total_scenario8_content['P_inject']
P_inject_sc_9 = total_scenario9_content['P_inject']
P_inject_sc_10 = total_scenario10_content['P_inject']

#
#The Data Visualisation
#

c_buy = 0.0002899; #euro/Wh
c_sell = 0.00015; #euro/Wh
delta_t = 0.25

energy_grid_sc_1 = sum([i[1] for i in P_grid_sc_1])*delta_t/1000
energy_grid_sc_2 = sum([i[1] for i in P_grid_sc_2])*delta_t/1000
energy_grid_sc_3 = sum([i[1] for i in P_grid_sc_3])*delta_t/1000
energy_grid_sc_4 = sum([i[1] for i in P_grid_sc_4])*delta_t/1000
energy_grid_sc_5 = sum([i[1] for i in P_grid_sc_5])*delta_t/1000
energy_grid_sc_6 = sum([i[1] for i in P_grid_sc_6])*delta_t/1000
energy_grid_sc_7 = sum([i[1] for i in P_grid_sc_7])*delta_t/1000
energy_grid_sc_8 = sum([i[1] for i in P_grid_sc_8])*delta_t/1000
energy_grid_sc_9 = sum([i[1] for i in P_grid_sc_9])*delta_t/1000
energy_grid_sc_10 = sum([i[1] for i in P_grid_sc_10])*delta_t/1000

energy_inject_sc_1 = sum([i[1] for i in P_inject_sc_1])*delta_t/1000
energy_inject_sc_2 = sum([i[1] for i in P_inject_sc_2])*delta_t/1000
energy_inject_sc_3 = sum([i[1] for i in P_inject_sc_3])*delta_t/1000
energy_inject_sc_4 = sum([i[1] for i in P_inject_sc_4])*delta_t/1000
energy_inject_sc_5 = sum([i[1] for i in P_inject_sc_5])*delta_t/1000
energy_inject_sc_6 = sum([i[1] for i in P_inject_sc_6])*delta_t/1000
energy_inject_sc_7 = sum([i[1] for i in P_inject_sc_7])*delta_t/1000
energy_inject_sc_8 = sum([i[1] for i in P_inject_sc_8])*delta_t/1000
energy_inject_sc_9 = sum([i[1] for i in P_inject_sc_9])*delta_t/1000
energy_inject_sc_10 = sum([i[1] for i in P_inject_sc_10])*delta_t/1000

total_cost_energy_sc_1 = sum([i[1] for i in P_grid_sc_1])*delta_t*c_buy
total_cost_energy_sc_2 = sum([i[1] for i in P_grid_sc_2])*delta_t*c_buy
total_cost_energy_sc_3 = sum([i[1] for i in P_grid_sc_3])*delta_t*c_buy
total_cost_energy_sc_4 = sum([i[1] for i in P_grid_sc_4])*delta_t*c_buy
total_cost_energy_sc_5 = sum([i[1] for i in P_grid_sc_5])*delta_t*c_buy
total_cost_energy_sc_6 = sum([i[1] for i in P_grid_sc_6])*delta_t*c_buy
total_cost_energy_sc_7 = sum([i[1] for i in P_grid_sc_7])*delta_t*c_buy
total_cost_energy_sc_8 = sum([i[1] for i in P_grid_sc_8])*delta_t*c_buy
total_cost_energy_sc_9 = sum([i[1] for i in P_grid_sc_9])*delta_t*c_buy
total_cost_energy_sc_10 = sum([i[1] for i in P_grid_sc_10])*delta_t*c_buy

total_income_energy_sc_1 = sum([i[1] for i in P_inject_sc_1])*delta_t*c_sell
total_income_energy_sc_2 = sum([i[1] for i in P_inject_sc_1])*delta_t*c_sell
total_income_energy_sc_3 = sum([i[1] for i in P_inject_sc_1])*delta_t*c_sell
total_income_energy_sc_4 = sum([i[1] for i in P_inject_sc_1])*delta_t*c_sell
total_income_energy_sc_5 = sum([i[1] for i in P_inject_sc_1])*delta_t*c_sell
total_income_energy_sc_6 = sum([i[1] for i in P_inject_sc_1])*delta_t*c_sell
total_income_energy_sc_7 = sum([i[1] for i in P_inject_sc_1])*delta_t*c_sell
total_income_energy_sc_8 = sum([i[1] for i in P_inject_sc_1])*delta_t*c_sell
total_income_energy_sc_9 = sum([i[1] for i in P_inject_sc_1])*delta_t*c_sell
total_income_energy_sc_10 = sum([i[1] for i in P_inject_sc_1])*delta_t*c_sell

total_profit_energy_sc_1 = total_cost_energy_sc_1 - total_income_energy_sc_1
total_profit_energy_sc_2 = total_cost_energy_sc_2 - total_income_energy_sc_2
total_profit_energy_sc_3 = total_cost_energy_sc_3 - total_income_energy_sc_3
total_profit_energy_sc_4 = total_cost_energy_sc_4 - total_income_energy_sc_4
total_profit_energy_sc_5 = total_cost_energy_sc_5 - total_income_energy_sc_5
total_profit_energy_sc_6 = total_cost_energy_sc_6 - total_income_energy_sc_6
total_profit_energy_sc_7 = total_cost_energy_sc_7 - total_income_energy_sc_7
total_profit_energy_sc_8 = total_cost_energy_sc_8 - total_income_energy_sc_8
total_profit_energy_sc_9 = total_cost_energy_sc_9 - total_income_energy_sc_9
total_profit_energy_sc_10 = total_cost_energy_sc_10 - total_income_energy_sc_10

#Data Visualition
width = 0.5 #line width for the plots
#data_range =500 #the data rangeof plots

start = dt.datetime(2018, 10, 1, 18, 0) #Starting time is accepted as 01.October.2018
time = [start + dt.timedelta(minutes = j*15) for j in range(len(P_B_ch_sc_1))]    

if os.path.isdir('/media/mert/D02A-A409/Figures/Stochastic/') == False:
    os.mkdir('/media/mert/D02A-A409/Figures/Stochastic/')
    destination = '/media/mert/D02A-A409/Figures/Stochastic/'
else:
    destination = '/media/mert/D02A-A409/Figures/Stochastic/'
    

file_name = "total_results_Stochastic"
complete_name = os.path.join(destination, file_name+".txt")
file = open(complete_name, "w+")
file.write("##########RESULTS##########\r\n")
file.write("Total energy drawn from grid for sc1 = %f kWh\r\n" %energy_grid_sc_1)
file.write("Total energy drawn from grid for sc2 = %f kWh\r\n" %energy_grid_sc_2)
file.write("Total energy drawn from grid for sc3 = %f kWh\r\n" %energy_grid_sc_3)
file.write("Total energy drawn from grid for sc4 = %f kWh\r\n" %energy_grid_sc_4)
file.write("Total energy drawn from grid for sc5 = %f kWh\r\n" %energy_grid_sc_5)
file.write("Total energy drawn from grid for sc6 = %f kWh\r\n" %energy_grid_sc_6)
file.write("Total energy drawn from grid for sc7 = %f kWh\r\n" %energy_grid_sc_7)
file.write("Total energy drawn from grid for sc8 = %f kWh\r\n" %energy_grid_sc_8)
file.write("Total energy drawn from grid for sc9 = %f kWh\r\n" %energy_grid_sc_9)
file.write("Total energy drawn from grid for sc10 = %f kWh\r\n" %energy_grid_sc_10)
file.write(" ")
file.write("Total energy inject to grid for sc1 = %f kWh\r\n" %energy_inject_sc_1)
file.write("Total energy inject to grid for sc2 = %f kWh\r\n" %energy_inject_sc_2)
file.write("Total energy inject to grid for sc3 = %f kWh\r\n" %energy_inject_sc_3)
file.write("Total energy inject to grid for sc4 = %f kWh\r\n" %energy_inject_sc_4)
file.write("Total energy inject to grid for sc5 = %f kWh\r\n" %energy_inject_sc_5)
file.write("Total energy inject to grid for sc6 = %f kWh\r\n" %energy_inject_sc_6)
file.write("Total energy inject to grid for sc7 = %f kWh\r\n" %energy_inject_sc_7)
file.write("Total energy inject to grid for sc8 = %f kWh\r\n" %energy_inject_sc_8)
file.write("Total energy inject to grid for sc9 = %f kWh\r\n" %energy_inject_sc_9)
file.write("Total energy inject to grid for sc10 = %f kWh\r\n" %energy_inject_sc_10)
file.write(" ")

file.write("Total energy cost for sc1 = %f €\r\n" %total_cost_energy_sc_1)
file.write("Total energy cost for sc2 = %f €\r\n" %total_cost_energy_sc_2)
file.write("Total energy cost for sc3 = %f €\r\n" %total_cost_energy_sc_3)
file.write("Total energy cost for sc4 = %f €\r\n" %total_cost_energy_sc_4)
file.write("Total energy cost for sc5 = %f €\r\n" %total_cost_energy_sc_5)
file.write("Total energy cost for sc6 = %f €\r\n" %total_cost_energy_sc_6)
file.write("Total energy cost for sc7 = %f €\r\n" %total_cost_energy_sc_7)
file.write("Total energy cost for sc8 = %f €\r\n" %total_cost_energy_sc_8)
file.write("Total energy cost for sc9 = %f €\r\n" %total_cost_energy_sc_9)
file.write("Total energy cost for sc10 = %f €\r\n" %total_cost_energy_sc_10)
file.write(" ")

file.write("Total energy income for sc1 = %f €\r\n" %total_income_energy_sc_1)
file.write("Total energy income for sc2 = %f €\r\n" %total_income_energy_sc_2)
file.write("Total energy income for sc3 = %f €\r\n" %total_income_energy_sc_3)
file.write("Total energy income for sc4 = %f €\r\n" %total_income_energy_sc_4)
file.write("Total energy income for sc5 = %f €\r\n" %total_income_energy_sc_5)
file.write("Total energy income for sc6 = %f €\r\n" %total_income_energy_sc_6)
file.write("Total energy income for sc7 = %f €\r\n" %total_income_energy_sc_7)
file.write("Total energy income for sc8 = %f €\r\n" %total_income_energy_sc_8)
file.write("Total energy income for sc9 = %f €\r\n" %total_income_energy_sc_9)
file.write("Total energy income for sc10 = %f €\r\n" %total_income_energy_sc_10)
file.write(" ")

file.write("Total profit for sc1 = %f €\r\n" %total_profit_energy_sc_1)
file.write("Total profit for sc2 = %f €\r\n" %total_profit_energy_sc_2)
file.write("Total profit for sc3 = %f €\r\n" %total_profit_energy_sc_3)
file.write("Total profit for sc4 = %f €\r\n" %total_profit_energy_sc_4)
file.write("Total profit for sc5 = %f €\r\n" %total_profit_energy_sc_5)
file.write("Total profit for sc6 = %f €\r\n" %total_profit_energy_sc_6)
file.write("Total profit for sc7 = %f €\r\n" %total_profit_energy_sc_7)
file.write("Total profit for sc8 = %f €\r\n" %total_profit_energy_sc_8)
file.write("Total profit for sc9 = %f €\r\n" %total_profit_energy_sc_9)
file.write("Total profit for sc10 = %f €\r\n" %total_profit_energy_sc_10)
file.write("#######################################")
file.close()


#model_demand1 = model.create_instance('/home/mert/optimization/pyomo_code/Stochastic/trial_two/scenariodata/Scenario1.dat')
#model_demand2 = model.create_instance('/home/mert/optimization/pyomo_code/Stochastic/trial_two/scenariodata/Scenario2.dat')
#model_demand3 = model.create_instance('/home/mert/optimization/pyomo_code/Stochastic/trial_two/scenariodata/Scenario3.dat')
#model_demand4 = model.create_instance('/home/mert/optimization/pyomo_code/Stochastic/trial_two/scenariodata/Scenario4.dat')
#model_demand5 = model.create_instance('/home/mert/optimization/pyomo_code/Stochastic/trial_two/scenariodata/Scenario5.dat')
#model_demand6 = model.create_instance('/home/mert/optimization/pyomo_code/Stochastic/trial_two/scenariodata/Scenario6.dat')
#model_demand7 = model.create_instance('/home/mert/optimization/pyomo_code/Stochastic/trial_two/scenariodata/Scenario7.dat')
#model_demand8 = model.create_instance('/home/mert/optimization/pyomo_code/Stochastic/trial_two/scenariodata/Scenario8.dat')
#model_demand9 = model.create_instance('/home/mert/optimization/pyomo_code/Stochastic/trial_two/scenariodata/Scenario9.dat')
#model_demand10 = model.create_instance('/home/mert/optimization/pyomo_code/Stochastic/trial_two/scenariodata/Scenario10.dat')

#Demand Scenarios
demand1 = pandas.pandas.read_excel('Scenario1.xlsx')
demand2 = pandas.read_excel('Scenario2.xlsx')
demand3 = pandas.read_excel('Scenario3.xlsx')
demand4 = pandas.read_excel('Scenario4.xlsx')
demand5 = pandas.read_excel('Scenario5.xlsx')
demand6 = pandas.read_excel('Scenario6.xlsx')
demand7 = pandas.read_excel('Scenario7.xlsx')
demand8 = pandas.read_excel('Scenario8.xlsx')
demand9 = pandas.read_excel('Scenario9.xlsx')
demand10 = pandas.read_excel('Scenario10.xlsx')

x1 = time
#x = pandas.DataFrame(range(0,96))

#Battery Charge Power
y_b1 = [i[1] for i in P_B_ch_sc_1]
y_b2 = [i[1] for i in P_B_ch_sc_2]
y_b3 = [i[1] for i in P_B_ch_sc_3]
y_b4 = [i[1] for i in P_B_ch_sc_4]
y_b5 = [i[1] for i in P_B_ch_sc_5]
y_b6 = [i[1] for i in P_B_ch_sc_6]
y_b7 = [i[1] for i in P_B_ch_sc_7]
y_b8 = [i[1] for i in P_B_ch_sc_8]
y_b9 = [i[1] for i in P_B_ch_sc_9]
y_b10 = [i[1] for i in P_B_ch_sc_10]

y_b1 = pandas.DataFrame(y_b1)
y_b2 = pandas.DataFrame(y_b2)
y_b3 = pandas.DataFrame(y_b3)
y_b4 = pandas.DataFrame(y_b4)
y_b5 = pandas.DataFrame(y_b5)
y_b6 = pandas.DataFrame(y_b6)
y_b7 = pandas.DataFrame(y_b7)
y_b8 = pandas.DataFrame(y_b8)
y_b9 = pandas.DataFrame(y_b9)
y_b10 = pandas.DataFrame(y_b10)

#Battery Discharge Power
y_b_dis1 = [i[1] for i in P_B_dis_sc_1]
y_b_dis2 = [i[1] for i in P_B_dis_sc_2]
y_b_dis3 = [i[1] for i in P_B_dis_sc_3]
y_b_dis4 = [i[1] for i in P_B_dis_sc_4]
y_b_dis5 = [i[1] for i in P_B_dis_sc_5]
y_b_dis6 = [i[1] for i in P_B_dis_sc_6]
y_b_dis7 = [i[1] for i in P_B_dis_sc_7]
y_b_dis8 = [i[1] for i in P_B_dis_sc_8]
y_b_dis9 = [i[1] for i in P_B_dis_sc_9]
y_b_dis10 = [i[1] for i in P_B_dis_sc_10]

y_b_dis1 = pandas.DataFrame(y_b_dis1)
y_b_dis2 = pandas.DataFrame(y_b_dis2)
y_b_dis3 = pandas.DataFrame(y_b_dis3)
y_b_dis4 = pandas.DataFrame(y_b_dis4)
y_b_dis5 = pandas.DataFrame(y_b_dis5)
y_b_dis6 = pandas.DataFrame(y_b_dis6)
y_b_dis7 = pandas.DataFrame(y_b_dis7)
y_b_dis8 = pandas.DataFrame(y_b_dis8)
y_b_dis9 = pandas.DataFrame(y_b_dis9)
y_b_dis10 = pandas.DataFrame(y_b_dis10)



plt.subplot(2, 1, 1)
plt.plot(range(0,96), demand1, label = 'Scenario1')
#plt.plot(range(0,96), demand2, label = 'Scenario2')
plt.plot(range(0,96), demand3, label = 'Scenario3')
#plt.plot(range(0,96), demand4, label = 'Scenario4')
plt.plot(range(0,96), demand5, label = 'Scenario5')
#plt.plot(range(0,96), demand6, label = 'Scenario6')
plt.plot(range(0,96), demand7, label = 'Scenario7')
#plt.plot(range(0,96), demand8, label = 'Scenario8')
plt.plot(range(0,96), demand9, label = 'Scenario9')
#plt.plot(range(0,96), demand10, label = 'Scenario10')
plt.plot(range(0,96), P_demand_portion, 'o', label = 'Base', markersize = 3)
plt.legend(loc = 1)
plt.title('Scenario Variations')
plt.ylabel('Demand (W)')

plt.subplot(2, 1, 2)
plt.plot(y_b1-y_b_dis1, label = 'Scenario1')
#plt.plot(-y_b_dis1, label = 'Scenario1')
#plt.plot(y_ev2, label = 'Scenario2')
plt.plot(y_b3-y_b_dis3, label = 'Scenario3')
#plt.plot(-y_b_dis3, label = 'Scenario3')
#plt.plot(y_ev4, label = 'Scenario4')
plt.plot(y_b5-y_b_dis5, label = 'Scenario5')
#plt.plot(-y_b_dis5, label = 'Scenario5')
#plt.plot(y_ev6, label = 'Scenario6')
plt.plot(y_b7-y_b_dis7, label = 'Scenario7')
#plt.plot(-y_b_dis7, label = 'Scenario7')
#plt.plot(y_ev8, label = 'Scenario8')
plt.plot(y_b9-y_b_dis9, label = 'Scenario9')
#plt.plot(-y_b_dis9, label = 'Scenario9')
#plt.plot(y_ev10, label = 'Scenario10')
plt.plot(P_B_portion, 'o', label = 'Base', markersize = 3)

plt.xlabel('Time Step(15 min)')
plt.ylabel('Battery Power (W)')

plt.tight_layout()
plt.savefig(destination + 'Demand_vs_Battery_Power', dpi=900)
plt.close()





#EV Charge Power
y_ev1 = [i[1] for i in P_EV_ch_sc_1]
y_ev2 = [i[1] for i in P_EV_ch_sc_2]
y_ev3 = [i[1] for i in P_EV_ch_sc_3]
y_ev4 = [i[1] for i in P_EV_ch_sc_4]
y_ev5 = [i[1] for i in P_EV_ch_sc_5]
y_ev6 = [i[1] for i in P_EV_ch_sc_6]
y_ev7 = [i[1] for i in P_EV_ch_sc_7]
y_ev8 = [i[1] for i in P_EV_ch_sc_8]
y_ev9 = [i[1] for i in P_EV_ch_sc_9]
y_ev10 = [i[1] for i in P_EV_ch_sc_10]

y_ev1 = pandas.DataFrame(y_ev1)
y_ev2 = pandas.DataFrame(y_ev2)
y_ev3 = pandas.DataFrame(y_ev3)
y_ev4 = pandas.DataFrame(y_ev4)
y_ev5 = pandas.DataFrame(y_ev5)
y_ev6 = pandas.DataFrame(y_ev6)
y_ev7 = pandas.DataFrame(y_ev7)
y_ev8 = pandas.DataFrame(y_ev8)
y_ev9 = pandas.DataFrame(y_ev9)
y_ev10 = pandas.DataFrame(y_ev10)

#Battery Discharge Power
y_ev_dis1 = [i[1] for i in P_EV_dis_sc_1]
y_ev_dis2 = [i[1] for i in P_EV_dis_sc_2]
y_ev_dis3 = [i[1] for i in P_EV_dis_sc_3]
y_ev_dis4 = [i[1] for i in P_EV_dis_sc_4]
y_ev_dis5 = [i[1] for i in P_EV_dis_sc_5]
y_ev_dis6 = [i[1] for i in P_EV_dis_sc_6]
y_ev_dis7 = [i[1] for i in P_EV_dis_sc_7]
y_ev_dis8 = [i[1] for i in P_EV_dis_sc_8]
y_ev_dis9 = [i[1] for i in P_EV_dis_sc_9]
y_ev_dis10 = [i[1] for i in P_EV_dis_sc_10]

y_ev_dis1 = pandas.DataFrame(y_ev_dis1)
y_ev_dis2 = pandas.DataFrame(y_ev_dis2)
y_ev_dis3 = pandas.DataFrame(y_ev_dis3)
y_ev_dis4 = pandas.DataFrame(y_ev_dis4)
y_ev_dis5 = pandas.DataFrame(y_ev_dis5)
y_ev_dis6 = pandas.DataFrame(y_ev_dis6)
y_ev_dis7 = pandas.DataFrame(y_ev_dis7)
y_ev_dis8 = pandas.DataFrame(y_ev_dis8)
y_ev_dis9 = pandas.DataFrame(y_ev_dis9)
y_ev_dis10 = pandas.DataFrame(y_ev_dis10)


plt.subplot(2, 1, 1)
plt.plot(range(0,96), demand1, label = 'Scenario1')
#plt.plot(range(0,96), demand2, label = 'Scenario2')
plt.plot(range(0,96), demand3, label = 'Scenario3')
#plt.plot(range(0,96), demand4, label = 'Scenario4')
plt.plot(range(0,96), demand5, label = 'Scenario5')
#plt.plot(range(0,96), demand6, label = 'Scenario6')
plt.plot(range(0,96), demand7, label = 'Scenario7')
#plt.plot(range(0,96), demand8, label = 'Scenario8')
plt.plot(range(0,96), demand9, label = 'Scenario9')
#plt.plot(range(0,96), demand10, label = 'Scenario10')
plt.plot(range(0,96), P_demand_portion, 'o', label = 'Base', markersize = 3)
plt.legend(loc = 1)
plt.title('Scenario Variations')
plt.ylabel('Demand (W)')

plt.subplot(2, 1, 2)
plt.plot(y_ev1-y_ev_dis1, label = 'Scenario1')
#plt.plot(-y_b_dis1, label = 'Scenario1')
#plt.plot(y_ev2, label = 'Scenario2')
plt.plot(y_ev3-y_ev_dis3, label = 'Scenario3')
#plt.plot(-y_b_dis3, label = 'Scenario3')
#plt.plot(y_ev4, label = 'Scenario4')
plt.plot(y_ev5-y_ev_dis5, label = 'Scenario5')
#plt.plot(-y_b_dis5, label = 'Scenario5')
#plt.plot(y_ev6, label = 'Scenario6')
plt.plot(y_ev7-y_ev_dis7, label = 'Scenario7')
#plt.plot(-y_b_dis7, label = 'Scenario7')
#plt.plot(y_ev8, label = 'Scenario8')
plt.plot(y_ev9-y_ev_dis9, label = 'Scenario9')
#plt.plot(-y_b_dis9, label = 'Scenario9')
#plt.plot(y_ev10, label = 'Scenario10')
plt.plot(range(0,96), P_EV_portion, 'o', label = 'Base', markersize = 3)

plt.xlabel('Time Step(15 min)')
plt.ylabel('EV Power (W)')

plt.tight_layout()
plt.savefig(destination + 'Demand_vs_EV_Power', dpi=900)
plt.close()

#Grid Power
y_grid1 = [i[1] for i in P_grid_sc_1]
y_grid2 = [i[1] for i in P_grid_sc_2]
y_grid3 = [i[1] for i in P_grid_sc_3]
y_grid4 = [i[1] for i in P_grid_sc_4]
y_grid5 = [i[1] for i in P_grid_sc_5]
y_grid6 = [i[1] for i in P_grid_sc_6]
y_grid7 = [i[1] for i in P_grid_sc_7]
y_grid8 = [i[1] for i in P_grid_sc_8]
y_grid9 = [i[1] for i in P_grid_sc_9]
y_grid10 = [i[1] for i in P_grid_sc_10]

y_grid1 = pandas.DataFrame(y_grid1)
y_grid2 = pandas.DataFrame(y_grid2)
y_grid3 = pandas.DataFrame(y_grid3)
y_grid4 = pandas.DataFrame(y_grid4)
y_grid5 = pandas.DataFrame(y_grid5)
y_grid6 = pandas.DataFrame(y_grid6)
y_grid7 = pandas.DataFrame(y_grid7)
y_grid8 = pandas.DataFrame(y_grid8)
y_grid9 = pandas.DataFrame(y_grid9)
y_grid10 = pandas.DataFrame(y_grid10)

#Inject Power
y_inject1 = [i[1] for i in P_inject_sc_1]
y_inject2 = [i[1] for i in P_inject_sc_2]
y_inject3 = [i[1] for i in P_inject_sc_3]
y_inject4 = [i[1] for i in P_inject_sc_4]
y_inject5 = [i[1] for i in P_inject_sc_5]
y_inject6 = [i[1] for i in P_inject_sc_6]
y_inject7 = [i[1] for i in P_inject_sc_7]
y_inject8 = [i[1] for i in P_inject_sc_8]
y_inject9 = [i[1] for i in P_inject_sc_9]
y_inject10 = [i[1] for i in P_inject_sc_10]

y_inject1 = pandas.DataFrame(y_inject1)
y_inject2 = pandas.DataFrame(y_inject2)
y_inject3 = pandas.DataFrame(y_inject3)
y_inject4 = pandas.DataFrame(y_inject4)
y_inject5 = pandas.DataFrame(y_inject5)
y_inject6 = pandas.DataFrame(y_inject6)
y_inject7 = pandas.DataFrame(y_inject7)
y_inject8 = pandas.DataFrame(y_inject8)
y_inject9 = pandas.DataFrame(y_inject9)
y_inject10 = pandas.DataFrame(y_inject10)


plt.subplot(2, 1, 1)
plt.plot(range(0,96), demand1, label = 'Scenario1')
#plt.plot(range(0,96), demand2, label = 'Scenario2')
plt.plot(range(0,96), demand3, label = 'Scenario3')
#plt.plot(range(0,96), demand4, label = 'Scenario4')
plt.plot(range(0,96), demand5, label = 'Scenario5')
#plt.plot(range(0,96), demand6, label = 'Scenario6')
plt.plot(range(0,96), demand7, label = 'Scenario7')
#plt.plot(range(0,96), demand8, label = 'Scenario8')
plt.plot(range(0,96), demand9, label = 'Scenario9')
#plt.plot(range(0,96), demand10, label = 'Scenario10')
plt.plot(range(0,96), P_demand_portion, 'o', label = 'Base', markersize = 3)
plt.legend(loc = 1)
plt.title('Scenario Variations')
plt.ylabel('Demand (W)')

plt.subplot(2, 1, 2)
plt.plot(y_grid1, label = 'Scenario1')
#plt.plot(-y_b_dis1, label = 'Scenario1')
#plt.plot(y_ev2, label = 'Scenario2')
plt.plot(y_grid3, label = 'Scenario3')
#plt.plot(-y_b_dis3, label = 'Scenario3')
#plt.plot(y_ev4, label = 'Scenario4')
plt.plot(y_grid5, label = 'Scenario5')
#plt.plot(-y_b_dis5, label = 'Scenario5')
#plt.plot(y_ev6, label = 'Scenario6')
plt.plot(y_grid7, label = 'Scenario7')
#plt.plot(-y_b_dis7, label = 'Scenario7')
#plt.plot(y_ev8, label = 'Scenario8')
plt.plot(y_grid9, label = 'Scenario9')

#plt.plot(-y_b_dis9, label = 'Scenario9')
#plt.plot(y_ev10, label = 'Scenario10')
plt.plot(range(0,96), P_grid_portion, 'o', label = 'Base', markersize = 3)

plt.xlabel('Time Step(15 min)')
plt.ylabel('Grid Power (W)')

plt.tight_layout()
plt.savefig(destination + 'Demand_vs_Grid_Power', dpi=900)
plt.close()


plt.subplot(2, 1, 1)
plt.plot(range(0,96), demand1, label = 'Scenario1')
#plt.plot(range(0,96), demand2, label = 'Scenario2')
plt.plot(range(0,96), demand3, label = 'Scenario3')
#plt.plot(range(0,96), demand4, label = 'Scenario4')
plt.plot(range(0,96), demand5, label = 'Scenario5')
#plt.plot(range(0,96), demand6, label = 'Scenario6')
plt.plot(range(0,96), demand7, label = 'Scenario7')
#plt.plot(range(0,96), demand8, label = 'Scenario8')
plt.plot(range(0,96), demand9, label = 'Scenario9')
#plt.plot(range(0,96), demand10, label = 'Scenario10')
plt.plot(range(0,96), P_demand_portion, 'o', label = 'Base', markersize = 3)
plt.legend(loc = 1)
plt.title('Scenario Variations')
plt.ylabel('Demand (W)')

plt.subplot(2, 1, 2)
plt.plot(y_inject1, label = 'Scenario1')
#plt.plot(-y_b_dis1, label = 'Scenario1')
#plt.plot(y_ev2, label = 'Scenario2')
plt.plot(y_inject3, label = 'Scenario3')
#plt.plot(-y_b_dis3, label = 'Scenario3')
#plt.plot(y_ev4, label = 'Scenario4')
plt.plot(y_inject5, label = 'Scenario5')
#plt.plot(-y_b_dis5, label = 'Scenario5')
#plt.plot(y_ev6, label = 'Scenario6')
plt.plot(y_inject7, label = 'Scenario7')
#plt.plot(-y_b_dis7, label = 'Scenario7')
#plt.plot(y_ev8, label = 'Scenario8')
plt.plot(y_inject9, label = 'Scenario9')
#plt.plot(-y_b_dis9, label = 'Scenario9')
#plt.plot(y_ev10, label = 'Scenario10')
plt.plot(range(0,96), P_inject_portion, 'o', label = 'Base', markersize = 3)

plt.xlabel('Time Step(15 min)')
plt.ylabel('Injected Power (W)')

plt.tight_layout()
plt.savefig(destination + 'Demand_vs_Injected_Power', dpi=900)
plt.close()

