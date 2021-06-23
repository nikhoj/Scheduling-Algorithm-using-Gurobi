from gurobipy import *

M = 10**3

jobs = ["Job_1", "Job_2", "Job_3"]
machines = ["MachineA", "MachineB", "MachineC", "MachineD"]

time_dict ={
    "Job_1": {"MachineA": 10, "MachineB": 8, "MachineC": 4},
    "Job_2": {"MachineB": 8, "MachineA": 3, "MachineD": 5, "MachineC": 6},
    "Job_3": {"MachineA": 4, "MachineB": 7, "MachineD": 3}
}

time_dict_coupled = {(machine,job): time_dict[job][machine] 
                     for job in jobs for machine in time_dict[job].keys()}

conflict_per_machine_dict = {machine: 
                             {job: time_dict_coupled[(machine,job)] 
                              for job in jobs if (machine,job) in time_dict_coupled.keys()}
                             for machine in machines}

m = Model("Job-Shop")

y = m.addVar(name="Makespan")
x = m.addVars(jobs,machines, name="Start_time_job_machine")
delta_12 = m.addVars(machines, vtype=GRB.BINARY, name="conflict_per_machine_job_12")
delta_13 = m.addVars(machines[:1], vtype=GRB.BINARY, name="conflict_per_machine_ob_13")
delta_23 = m.addVars(machines[:1], vtype=GRB.BINARY, name="conflict_per_machine_ob_23")

m.setObjective(y, GRB.MINIMIZE)

m.addConstrs((y >= x[job,list(time_dict[job].keys())[-1]] 
              + time_dict[job][list(time_dict[job].keys())[-1]] 
              for job in jobs), name="makespan_constraint")

m.addConstrs((x[job,list(time_dict[job].keys())[-machine_index+1]] >= 
              x[job,list(time_dict[job].keys())[-machine_index]] 
              + time_dict[job][list(time_dict[job].keys())[-machine_index]]
              for job in jobs for machine_index in range(2,len(time_dict[job])+1)), name="job_conflict_constraint")

m.addConstrs((x[list(conflict_per_machine_dict[machine].keys())[0],machine]
              + time_dict[list(conflict_per_machine_dict[machine].keys())[0]][machine] 
              - x[list(conflict_per_machine_dict[machine].keys())[1],machine] 
              <= M*(1-delta_12[machine]) for machine in machines), name="Conflict_pos_12")

m.addConstrs((x[list(conflict_per_machine_dict[machine].keys())[1],machine]
              + time_dict[list(conflict_per_machine_dict[machine].keys())[1]][machine] 
              - x[list(conflict_per_machine_dict[machine].keys())[0],machine] 
              <= M*delta_12[machine] 
              for machine in machines), name="Conflict_pos_21")

m.addConstrs((x[list(conflict_per_machine_dict[machine].keys())[0],machine]
              + time_dict[list(conflict_per_machine_dict[machine].keys())[0]][machine] 
              - x[list(conflict_per_machine_dict[machine].keys())[2],machine] 
              <= M*(1-delta_13[machine])
              for machine in machines[:1]) , name="Conflict_pos_13")

m.addConstrs((x[list(conflict_per_machine_dict[machine].keys())[2],machine]
              + time_dict[list(conflict_per_machine_dict[machine].keys())[2]][machine] 
              - x[list(conflict_per_machine_dict[machine].keys())[0],machine] 
              <= M*delta_13[machine] 
              for machine in machines[:1] ), name="Conflict_pos_31")

m.addConstrs((x[list(conflict_per_machine_dict[machine].keys())[1],machine]
              + time_dict[list(conflict_per_machine_dict[machine].keys())[1]][machine] 
              - x[list(conflict_per_machine_dict[machine].keys())[2],machine] 
              <= M*(1-delta_23[machine])
              for machine in machines[:1] ), name="Conflict_pos_23")

m.addConstrs((x[list(conflict_per_machine_dict[machine].keys())[2],machine]
              + time_dict[list(conflict_per_machine_dict[machine].keys())[2]][machine] 
              - x[list(conflict_per_machine_dict[machine].keys())[1],machine] 
              <= M*delta_23[machine] 
              for machine in machines[:1]), name="Conflict_pos_32")

m.optimize()

if m.status == GRB.OPTIMAL:   
    print("\n\n\nThe makespan is equal to %g" % m.objVal,"\n\n")
    for job in jobs:
        print("Optimal schedule of job", job[-1]+":")
        for machine in time_dict[job].keys():
            print( "\tstart on machine", machine[-1], "at time", "%.1f" %x[job,machine].X, "and end at",
                  "%.1f" %(x[job,machine].X+time_dict[job][machine])) 
        print("\n")
else:
    print('Optimum not found. Gurobi status code: ',m.status)
