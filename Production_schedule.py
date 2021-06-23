# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 16:54:36 2019

@author: Shuvro
"""

from gurobipy import *
import numpy as np
#dataset
demand = [800, 900, 1100, 400, 700, 1100, 700, 900, 800, 700, 800, 1100]
month_name = ["January","February","March","April","May","June","July","August","September","October","November","December"]
period = len(demand)
months = [i for i in range(1,period+1)]
prodmode = ["regular", "overtime"]
modes = [j for j in range(1,len(prodmode)+1)]
sellmonths = [k for k in range(1,period+1)]
capacity = [800,200]
prodcost= [10,12]
holdcost = [1,1]

#name of the model
m = Model ("Project_productionplanning")

#variable
x = m.addVars(months,modes,sellmonths, name = "Production")

#objective function
m.setObjective(quicksum((prodcost[j-1]*quicksum(x[i,j,k] for i in months for k in range(i,13)))for j in modes) + 
               quicksum(holdcost[j-1]*(k-i)*x[i,j,k] for j in modes for i in months for k in range(i,13)),GRB.MINIMIZE)
#constraints
m.addConstrs((quicksum(x[i,j,k] for j in modes for i in range(1,k+1)) == demand[k-1] if k <= 2 else
              quicksum(x[i,j,k] for j in modes for i in range(k-2,k+1)) == demand[k-1]) for k in sellmonths)

m.addConstrs((quicksum(x[i,j,k] for k in range(i,13)) <= capacity[j-1] if i >= 11 else
              quicksum(x[i,j,k] for k in range(i,i+3)) <= capacity[j-1]) for j in modes for i in months)
#optimization
m.optimize()
m.printAttr('x')
a = m.getAttr("x", m.getVars())
zeroset = np.zeros((12,2,12))
value = np.array(a).reshape((12,2,12))

if m.status == GRB.OPTIMAL:
    print("\n\n\nOptimal total production and storage cost for the next 12 months is equal to $%d" % m.objVal, "\n\n")
    for i in months:
        for j in modes:
            for k in sellmonths:
                if value[i-1,j-1,k-1] != 0:
                     if j==1:
                         print("In month "+str(month_name[i-1])+":","\n"
                               "\t""Produce "+str(value[i-1,j-1,k-1])+" units in regular mode to sell in"+" month "+str(month_name[k-1])+".")
                     else:
                         print("\t""Produce "+ str(value[i-1,j-1,k-1])+" units in overtime mode to sell in"+" month "+str(month_name[k-1])+".")
else:
    print('Optimum not found. Gurobi status code: ',m.status)

m.write("Production_plan.sol")
m.write("Production_plan.lp")