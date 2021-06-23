from gurobipy import *
import numpy as np

num_of_jobs = 3
num_of_machines = 4

process_time = np.array([[10,8,4,0],[3,8,6,5],[4,7,0,3]])

jobs = np.arange(0,num_of_jobs)
machines = np.arange(0,num_of_machines)
positions = np.arange(0,num_of_jobs)

m = Model("Flow_shop")
x = m.addVars(jobs,positions, vtype=GRB.BINARY, name="job_assign")
s = m.addVars(positions,machines, name="starting_time")


obj = s[positions[-1],machines[-1]] + quicksum((process_time[j,machines[-1]]*x[j,positions[-1]]) for j in jobs)
m.setObjective(obj, GRB.MINIMIZE)

m.addConstrs((quicksum(x[j,p] for j in jobs)) == 1 for p in positions)
m.addConstrs((quicksum(x[j,p] for p in positions)) == 1 for j in jobs)
m.addConstr(s[positions[0],machines[0]] == 0)
m.addConstrs(s[p,m] >= s[p-1,m] + quicksum(process_time[j,m]*x[j,p-1] for j in jobs)for p in positions[1:] for m in machines[1:])
m.addConstrs(s[p,m] >= s[p,m-1] + quicksum(process_time[j,m-1]*x[j,p] for j in jobs)for p in positions[1:] for m in machines[1:])
m.addConstrs(s[p,m+1] >= s[p,m] + quicksum(process_time[j,m]*x[j,p] for j in jobs)for p in positions[:1] for m in machines[:-1])
m.addConstrs(s[p+1,m] >= s[p,m] + quicksum(process_time[j,m]*x[j,p] for j in jobs)for p in positions[:-1] for m in machines[:1])
m.addConstrs(s[p,m] >= s[p-1,m+1]for p in positions[1:] for m in machines[:-1])

m.optimize()
m.printAttr('x')

if m.status == GRB.OPTIMAL:   
    print("\n\nOptimal makespan is equal to %.1f" % m.objVal)
    dict1 = {p:{j:x[j,p].X for j in jobs} for p in positions}
    dict2 = {0:'job1',1:'job2',2:'job3'}
    dict3 = {0:'position1',1:'position2',2:'position3'}
    dict4 = {dict3[p]: dict2[j] for p in positions for j in jobs if dict1[p][j]==1}
    print("\n\nThe optimal sequence of jobs:\n\n",dict4)
    print("\n",list(dict4.values()))
else:    print('Optimum not found. Gurobi status code: ',m.status)