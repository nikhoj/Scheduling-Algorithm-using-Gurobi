
from gurobipy import *
import numpy as np

Required_Hours = [[5000,5600,4000,6800,6000,3200],
                  [3750,2040,4875,2235,2505,1125],
                  [1440,2280,660,450,756,270]]
hours_array = np.array(Required_Hours).transpose()
product = [i for i in range(1,len(hours_array[0])+1)]
months = [i for i in range(1,len(hours_array[:])+1)]
days = [22,20,19,24,21,17]
worker_type = ["fixed", "local"]
worker = [i for i in range(1,len(worker_type)+1)]
reg_hour_salary = [8.5,11]
ot_hour_salary = [14,11]
regular_hour = 7
reg_worker = 46


m = Model("Hiring_schedule")
N = m.addVars(worker,months, vtype=GRB.INTEGER, name="num_of_worker in months")
O = m.addVars(worker,months,vtype=GRB.INTEGER,name="OT_worker_hour in month")

#Objective function
m.setObjective((quicksum((N[j,k]*regular_hour*days[k-1]*reg_hour_salary[j-1]
                + O[j,k]*ot_hour_salary[j-1]) for j in worker for k in months)),GRB.MINIMIZE)
#Constraints
m.addConstrs((N[j,k] == reg_worker if j == 1 else
              N[j,k] <= 30) for j in worker for k in months)
m.addConstrs((O[j,k] <= (24-regular_hour)*N[j,k]*days[k-1]) for j in worker for k in months)
m.addConstrs((quicksum((N[j,k]*regular_hour*days[k-1]+O[j,k]) for j in worker)
             >= (quicksum(hours_array[k-1][i] for i in range(len(hours_array[0]))))) for k in months)
#Optimization
m.optimize()
m.printAttr('x')

if m.status == GRB.OPTIMAL:   
    print("\nThe Optimal Cost is $ %d" % m.objVal)
else:
    print('Optimum not found. Gurobi status code: ',m.status)
    
