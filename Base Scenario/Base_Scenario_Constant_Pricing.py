#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  1 20:16:21 2019

@author: mert
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 28 19:45:03 2018

@author: mert
"""

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import os
import pandas
import numpy
import datetime as dt
from dateutil.relativedelta import *

#
#Input Parameters
#
availability_data = pandas.read_excel('ev.xlsx')
pv_data = pandas.read_excel('pv.xlsx')*1000
demand_data = pandas.read_excel('ph.xlsx')*1000

P_pv = pv_data.values
P_demand = demand_data.values
availability = availability_data.values

#
#Time Parameters
#
total_time = 24*4*365
delta_t = 1.0/4.0;  #time coefficient represents the 15 minutesin hour
one_week = 96*7
shift_week = 0

#
#Cost of Energy
#
c_buy = 0.0002899; #euro/Wh
c_sell = 0.00015; #euro/Wh

#
#Reluctant Power Matrice
#
P_reluctant = numpy.zeros(total_time)

#
#Home Battery Control Constants
#
P_B_max = 11.2e3 #W
P_B_min = 3.7 #W
E_B_min = 1.5e3 #Wh
E_B_max = 8.8e3 #Wh
E_B_0 = 5e3 #Wh
E_B_init = E_B_0
SOC_B_init = E_B_0/E_B_max
n_B_ch = 0.9 #battery charging efficiency
n_B_dis = n_B_ch #battery discharging efficiency
charge_power_B = 0
discharge_power_B = 0

#
#Battery Solution Matrices
#
P_B_ch = numpy.zeros(total_time)
P_B_dis = numpy.zeros(total_time)
E_b = numpy.zeros(total_time)
SOC_b = numpy.zeros(total_time)

#
#Battery Charge Function
#
def E_B_charge(time, charge_power_B): #this function accepts the time step and the charge power value of battery as a parameter. 
    if time > 0:
        E_b[time] = E_b[time-1] + (charge_power_B*n_B_ch*delta_t) #Battery Energy Calculation function in W/h
        if E_b[time] > E_B_max: #Charge Power Limitation condition 
            charge_power_B = (E_B_max - E_b[time-1])/(n_B_ch*delta_t) #Re-calculatethe charge power inorder not to exceed 
                                                                      #the maximum battery capacity 
            E_b[time] = E_B_max
    else:
        E_b[time] = E_B_0 + (charge_power_B*n_B_ch*delta_t)
        if E_b[time] > E_B_max:
            charge_power_B = (E_B_max - E_B_0)/(n_B_ch*delta_t)
            E_b[time] = E_B_max
    
    return charge_power_B

#
#Battery Discharge Function
#
def E_B_discharge(time, discharge_power_B):
    if time > 0:
        E_b[time] = E_b[time-1] - (discharge_power_B * delta_t/n_B_dis)
        if E_b[time] < E_B_min:
            discharge_power_B = (E_b[time-1] - E_B_min)*n_B_dis/delta_t
            E_b[time] = E_B_min
    else:
        E_b[time] = E_B_0 - (discharge_power_B * delta_t/n_B_dis)
        if E_b[time] < E_B_min:
            discharge_power_B = (E_B_0 - E_B_min)*n_B_dis/delta_t
            E_b[time] = E_B_min
    
    return discharge_power_B

#
#Battery Energy Level Update
#
def E_B_update(time, charge_power_B, discharge_power_B):
    if time > 0:
        E_b[time] = E_b[time-1] + (charge_power_B*n_B_ch*delta_t) - (discharge_power_B * delta_t/n_B_dis)
    else:
        E_b[time] = E_B_0 + (charge_power_B*n_B_ch*delta_t) - (discharge_power_B * delta_t/n_B_dis)
        
    return E_b[time]



#
#EV(BMW i3) Battery Control Constants #https://www.bmw.com.tr/tr/all-models/bmw-i/i3/2017/range-charging-efficiency.html
#
P_EV_max = 11e3 #Allowed power output of charger in Watts
E_EV_min = 6e3 #https://ev-database.uk/car/1104/BMW-i3 in Wh
E_EV_max = 33e3 #in Wh
E_EV_0 = 15e3 #in Wh
E_EV_init = E_EV_0 #initial Energy value of the EV value for the first iteration in W/h
SOC_EV_init = E_EV_0/E_EV_max #initial State os Charge value for the first iteration
n_EV_ch = 0.9 #EV charge efficiency
n_EV_dis = n_EV_ch #EV discharge efficiency
n_EV_drive = 0.7 #EV drive efficiency
E_EV_goal = 26.4e3 #EV goal energy value Wh
P_EV_drive = 1.2e3 #https://www.holmgrensbil.se/globalassets/nya-bilar/bmw/modellsidor/i3/dokument/i3-psl-eal_web.pdf in Watts
SOC_EV_goal = 0.8 #Goal SOC in percentage
SOC_EV_max = 1 #Maximum State of Charge



#
#EV solution matrices
#
P_EV_ch = numpy.zeros(total_time)
P_EV_ch_bat = numpy.zeros(total_time)
P_EV_dis = numpy.zeros(total_time)
P_EV_drive_sol = numpy.zeros(total_time)
E_ev = numpy.zeros(total_time)
SOC_ev = numpy.zeros(total_time)
SOC_EV_init = E_EV_0/E_EV_max

#
#EV Charge Function
#    
def E_EV_charge(time, charge_power_EV, Vehicle_Availability, EV_Energy_Level):
    if Vehicle_Availability == 1 and EV_Energy_Level < E_EV_max:
        if time > 0:
            E_ev[time] = E_ev[time-1] + (charge_power_EV*n_EV_ch*delta_t)
            if E_ev[time] > E_EV_max:
                charge_power_EV = (E_EV_max - E_ev[time-1])/(n_EV_ch*delta_t)
                E_ev[time] = E_EV_max
        else:
            E_ev[time] = E_EV_0 + (charge_power_EV*n_EV_ch*delta_t)
            if E_ev[time] > E_EV_max:
                charge_power_EV = (E_EV_max - E_EV_0)/(n_EV_ch*delta_t)
                E_ev[time] = E_EV_max
        return charge_power_EV
    else:
        charge_power_EV = 0 
        return charge_power_EV

#
#EV Discharge Function    
#
def E_EV_discharge(time, discharge_power_EV, Vehicle_Availability, EV_Energy_Level):
    if Vehicle_Availability == 0 and EV_Energy_Level > E_EV_min:
        if time > 0:
            E_ev[time] = E_ev[time-1] - (discharge_power_EV*delta_t/n_EV_drive)
            if E_ev[time] < E_EV_min:
                discharge_power_EV = (E_ev[time-1] - E_EV_min )*(n_EV_drive/delta_t)
                E_ev[time] = E_EV_min
        else:
            E_ev[time] = E_EV_0 - (discharge_power_EV*delta_t/n_EV_drive)
            if E_ev[time] > E_EV_max:
                discharge_power_EV = (E_EV_0 - E_EV_min)*(n_EV_drive/delta_t)
                E_ev[time] = E_EV_min
        return discharge_power_EV
    else:
        discharge_power_EV = 0
        return discharge_power_EV

#
#EV Energy Level Update
#
def E_EV_update(time, charge_power_EV, discharge_power_EV):
    if time > 0:
        E_ev[time] = E_ev[time-1] + (charge_power_EV*n_EV_ch*delta_t) - (discharge_power_EV * delta_t/n_EV_dis) 
    else:
        E_ev[time] = E_B_0 + (charge_power_EV*n_B_ch*delta_t) - (discharge_power_B * delta_t/n_B_dis) 
        
    return E_ev[time]    

#
#EV Cruise Function
#

def E_EV_cruise(time, drive_power_EV):
    if time > 0: 
        E_ev[time] = E_ev[time-1] - (drive_power_EV)/n_EV_drive*delta_t
    else:
        E_ev[time] = E_EV_0 - (drive_power_EV/n_EV_drive*delta_t)

    return drive_power_EV

        
#
#Grid Constants
#
P_grid_max = 33000.0 #in Watts
P_inject_max = 33000.0 #in Watts

#
#Grid solution matrices
#
P_grid = numpy.zeros(total_time)
P_grid_EV = numpy.zeros(total_time)
P_grid_house = numpy.zeros(total_time)
P_inject = numpy.zeros(total_time)
P_pv_demand_reluctant = numpy.zeros(total_time)

#
#Battery Charge Command
#
def Battery_Charge_Command(Battery_Energy_Level):
    if Battery_Energy_Level < E_B_max:
        return True
    else:
        return False

#
#Battery Discharge Command
#
def Battery_Discharge_Command(Battery_Energy_Level):
    if Battery_Energy_Level > E_B_min:
        return True
    else:
        return False
    
#
#EV Charge Command
#
def EV_Charge_Command(Vehicle_Availability, EV_Energy_Level):
    if Vehicle_Availability == 1 and EV_Energy_Level < E_EV_max:
        return True
    else:
        return False
    

#
#PowerBalance
#
Power_balance = numpy.zeros(total_time)

#
#For the Stochastic Optimization
#
#E_ev[26279] = E_EV_0 ##Comment this part out
#E_b[26279] = E_B_0 ##Comment this part out

for time in range(0, total_time): #range(26280, 26376) for the stochastic optimization
    if time == 0:
        #EV Charge-Discharge Decision
        P_EV_ch[time] = E_EV_charge(time, P_EV_max, availability[time], E_EV_init)
        P_EV_dis[time] = E_EV_discharge(time, P_EV_drive, availability[time], E_EV_init)
        E_ev[time] = E_EV_update(time, P_EV_ch[time], P_EV_dis[time])
        P_reluctant[time] = P_pv[time] - P_demand[time] - P_EV_ch[time]
        
        #Battery Charge-Discharge Decision
        if P_reluctant[time] > 0:
            if Battery_Charge_Command(E_B_init) == True:
                P_B_ch[time] = E_B_charge(time, P_reluctant[time])
                E_b[time] = E_B_update(time, P_B_ch[time], P_B_dis[time])
            else:
                E_b[time] = E_B_init
        elif P_reluctant[time] <= 0:
            if Battery_Discharge_Command(E_B_init) == True:
                battery_discharge_power = P_B_max + P_reluctant[time]
                if battery_discharge_power < 0:
                    battery_discharge_power = P_B_max
                P_B_dis[time] = E_B_discharge(time, battery_discharge_power)
                E_b[time] = E_B_update(time, P_B_ch[time], P_B_dis[time])
            else:
                E_b[time] = E_B_init
        P_grid[time] = P_EV_ch[time] + P_demand[time] - P_pv[time] - P_B_dis[time]
        if P_grid[time] < 0:
            P_inject[time] = -1*P_grid[time]
            P_grid[time] = 0
    
    #Calculations without initial Conditions
    elif time > 0:
        
        #EV Charge-Discharge Decision
        P_EV_ch[time] = E_EV_charge(time, P_EV_max, availability[time], E_ev[time-1])
        P_EV_dis[time] = E_EV_discharge(time, P_EV_drive, availability[time], E_ev[time-1])
        E_ev[time] = E_EV_update(time, P_EV_ch[time], P_EV_dis[time])
        P_reluctant[time] = P_pv[time] - P_demand[time] - P_EV_ch[time]
    
        #Battery Charge-Discharge Decision
        if P_reluctant[time] > 0:
            if Battery_Charge_Command(E_b[time-1]) == True:
                P_B_ch[time] = E_B_charge(time, P_reluctant[time])
                E_b[time] = E_B_update(time, P_B_ch[time], P_B_dis[time])
            else:
                E_b[time] = E_b[time-1]
        elif P_reluctant[time] <= 0:
            if Battery_Discharge_Command(E_b[time-1]) == True:
                battery_discharge_power = P_B_max + P_reluctant[time]
                if battery_discharge_power < 0:
                    battery_discharge_power = P_B_max                
                P_B_dis[time] = E_B_discharge(time, battery_discharge_power)
                E_b[time] = E_B_update(time, P_B_ch[time], P_B_dis[time])
            else:
                E_b[time] = E_b[time-1]
        
    #Grid and Inject Power Claculation
    P_grid[time] = P_EV_ch[time] + P_demand[time] - P_pv[time] - P_B_dis[time] + P_B_ch[time]
    if P_grid[time] < 0:
        P_inject[time] = -1*P_grid[time]
        P_grid[time] = 0
        
    #Power Balance Check
    Power_balance[time] = P_grid[time] + P_pv[time] + P_B_dis[time] - P_EV_ch[time] -P_demand[time] - P_B_ch[time] - P_inject[time] 
             
    #SOC Calculations
    SOC_b[time] = E_b[time]/E_B_max
    SOC_ev[time] = E_ev[time]/E_EV_max
        
#Total Results File

energy_grid = sum(P_grid)*delta_t/1000
energy_inject = sum(P_inject)*delta_t/1000
maximum_energy_grid = max(P_grid)*delta_t/1000
maximum_energy_inject = max(P_inject)*delta_t/1000
maximum_SOC_Battery = max(SOC_b)*100
minimum_SOC_Battery = min(SOC_b)*100
maximum_SOC_EV = max(SOC_ev)*100
minimum_SOC_EV = min(SOC_ev)*100
total_cost_energy = sum(P_grid)*delta_t*c_buy
total_income_energy = sum(P_inject)*delta_t*c_sell
total_profit_energy = (-sum(P_grid)*delta_t*c_buy + sum(P_inject)*delta_t * c_sell) 

#Data Visualition
width = 0.5 #line width for the plots
data_range =500 #the data rangeof plots

start = dt.datetime(2018, 1, 1, 0, 0) #Starting time is accepted as 01.January.2018
time = [start + dt.timedelta(minutes = j*15) for j in range(len(E_b))]    

#
#DO NOT FORGET TO CHANGE THE DIRECTORY TO SAVE THE RESULTS IN YOUR COMPUTER!!
#
 
if os.path.isdir('/media/mert/D02A-A409/Figures/Base_Scenario_Constant') == False:
    os.mkdir('/media/mert/D02A-A409/Figures/Base_Scenario_Constant')
    destination = '/media/mert/D02A-A409/Figures/Base_Scenario_Constant'
else:
    destination = '/media/mert/D02A-A409/Figures/Base_Scenario_Constant'
   
    
#Numerical Value File Creation
file_name = "total_results"
complete_name = os.path.join(destination, file_name+".txt")
file = open(complete_name, "w+")
file.write("##########RESULTS##########\r\n")
file.write("Total energy drawn from grid = %f kWh\r\n" %energy_grid)
file.write("Total energy inject to grid = %f kWh\r\n" %energy_inject)
file.write("Maximum energy drawn from grid = %f kWh\r\n" %maximum_energy_grid)
file.write("Maximum energy inject to grid = %f kWh\r\n" %maximum_energy_inject)
file.write("Maximum SOC of Battery = %f\r\n" %maximum_SOC_Battery)
file.write("Minimum SOC of Battery = %f\r\n" %minimum_SOC_Battery)
file.write("Maximum SOC of EV = %f \r\n" %maximum_SOC_EV)
file.write("Minimum SOC of EV = %f \r\n" %minimum_SOC_EV)
file.write("Total energy cost = %f $/kWh\r\n" %total_cost_energy)
file.write("Total energy income = %f $/kWh\r\n" %total_income_energy)
file.write("Total profit = %f $/kWh\r\n" %total_profit_energy)
file.write("#######################################")
file.close()            


#Plotting if necessary
"""
for j in range(0, 52+1):
    

#Creative and Defining Figures
    fig_P_EV_check = plt.plot(time[0+shift_week:one_week+shift_week], P_EV_ch[0+shift_week:one_week+shift_week], linewidth=width, label = 'EV Power')
    fig_EV_availability = plt.plot(time[0+shift_week:one_week+shift_week], availability[0+shift_week:one_week+shift_week]*10000, linewidth=width, label = 'EV availability')
    plt.gcf().autofmt_xdate()
    plt.title('EV Check for Base Scenario')
    plt.legend()
    plt.xlabel('Opt. Periods(15min)')
    plt.ylabel('Power(W)')
    plt.savefig(destination + '/fig_EV_check_'+str(j+1)+'_th_week.png', dpi=900)
    plt.close()

#House + PV
    fig_House = plt.plot(time[0+shift_week:one_week+shift_week], P_demand[0+shift_week:one_week+shift_week], linewidth=width, label = 'House')
    fig_PV = plt.plot(time[0+shift_week:one_week+shift_week], -P_pv[0+shift_week:one_week+shift_week], linewidth=width, label = 'PV')
    plt.gcf().autofmt_xdate()
    plt.title('House Demand and PV Generation for Base Scenario')
    plt.legend()
    plt.xlabel('Opt. Periods(15min)')
    plt.ylabel('Power(W)')
    plt.savefig(destination + '/fig_House_and_PV'+str(j+1)+'_th_week.png', dpi=900)
    plt.close()

#House + PV + Battery
    fig_House = plt.plot(time[0+shift_week:one_week+shift_week], P_demand[0+shift_week:one_week+shift_week], linewidth=width, label = 'House')
    fig_PV = plt.plot(time[0+shift_week:one_week+shift_week], -P_pv[0+shift_week:one_week+shift_week], linewidth=width, label = 'PV')
    fig_P_B = plt.plot(time[0+shift_week:one_week+shift_week], P_B_ch[0+shift_week:one_week+shift_week] - P_B_dis[0+shift_week:one_week+shift_week], linewidth=width, label = 'Battery')
    plt.gcf().autofmt_xdate()
    plt.title('House Demand, PV Generation and Battery Power for Base Scenario')
    plt.legend()
    plt.xlabel('Opt. Periods(15min)')
    plt.ylabel('Power(W)')
    plt.tight_layout()
    plt.savefig(destination + '/fig_House_PV_and_Battery'+str(j+1)+'_th_week.png', dpi=900)
    plt.close()

#House + PV + EV
    fig_House = plt.plot(time[0+shift_week:one_week+shift_week], P_demand[0+shift_week:one_week+shift_week], linewidth=width, label = 'House')
    fig_PV = plt.plot(time[0+shift_week:one_week+shift_week], -P_pv[0+shift_week:one_week+shift_week], linewidth=width, label = 'PV')
    fig_P_EV = plt.plot(time[0+shift_week:one_week+shift_week], P_EV_ch[0+shift_week:one_week+shift_week], linewidth=width, label = 'EV')
    plt.gcf().autofmt_xdate()
    plt.title('House Demand, PV Generation and EV Power for Base Scenario')
    plt.legend()
    plt.xlabel('Opt. Periods(15min)')
    plt.ylabel('Power(W)')
    plt.savefig(destination + '/fig_House_PV_and_EV'+str(j+1)+'_th_week.png', dpi=900)
    plt.close()

#Grid + Inject
    fig_P_grid = plt.plot(time[0+shift_week:one_week+shift_week], P_grid[0+shift_week:one_week+shift_week], linewidth=width, label = 'Grid Power')
    fig_P_inject = plt.plot(time[0+shift_week:one_week+shift_week], -P_inject[0+shift_week:one_week+shift_week], linewidth=width, label = 'Injected Power')
    plt.gcf().autofmt_xdate()
    plt.title('Grid and Inject Power for Base Scenario')
    plt.legend()
    plt.xlabel('Opt. Periods(15min)')
    plt.ylabel('Power(W)')
    plt.savefig(destination + '/fig_P_grid_and_P_inject'+str(j+1)+'_th_week.png', dpi=900)
    plt.close()

#Savings
    fig_P_grid_price = plt.plot(time[0+shift_week:one_week+shift_week], -1*P_grid[0+shift_week:one_week+shift_week]*c_buy*delta_t, linewidth=width, label = 'Cost')
    fig_P_inject_price = plt.plot(time[0+shift_week:one_week+shift_week], P_inject[0+shift_week:one_week+shift_week]*c_sell*delta_t, linewidth=width, label = 'Earnings')
    #fig_price_difference = plt.plot(time[0+shift_week:one_week+shift_week], -P_grid_sol[0+shift_week:one_week+shift_week]*c_buy*delta_t + P_inject_sol[0+shift_week:one_week+shift_week]*c_sell*delta_t, 'r--', label = 'Profit')
    plt.gcf().autofmt_xdate()
    plt.title('Energy Cost and Earnings for Base Scenario')
    plt.legend()
    plt.xlabel('Opt. Periods(15min)')
    plt.ylabel('Price($/Wh)')
    plt.savefig(destination + '/fig_Price'+str(j+1)+'_th_week.png', dpi=900)
    plt.close()    

    shift_week = shift_week + one_week
"""