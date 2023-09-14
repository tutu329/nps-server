from gurobipy import *
# from pyomo.environ import *


def main():
    # model = ConcreteModel()
    # # t_solver = SolverFactory('cplex')
    # t_solver = SolverFactory('gurobi')
    # solver_result = t_solver.solve(
    #     model,
    #     tee=True  # 输出中间结果
    # )

    # Create a new model
    m = Model("mip1")

    # Create variables
    x = m.addVar(vtype=GRB.BINARY, name="x")
    y = m.addVar(vtype=GRB.BINARY, name="y")
    z = m.addVar(vtype=GRB.BINARY, name="z")

    # Set objective
    m.setObjective(x + y + 2 * z, GRB.MAXIMIZE)

    # Add constraint: x + 2 y + 3 z <= 4
    m.addConstr(x + 2 * y + 3 * z <= 4, "c0")

    # Add constraint: x + y >= 1
    m.addConstr(x + y >= 1, "c1")

    m.optimize()

    for v in m.getVars():
        print(v.varName, v.x)

    print('Obj:', m.objVal)

if __name__ == "__main__" :
    main()
