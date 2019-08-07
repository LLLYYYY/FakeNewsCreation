import cplex
import sys
from DataStructure import *
from Multi_Dimension import *
from cplex.exceptions.errors import *

k = 30
e = 0.001
ci = 2
M = 10000

def hyperPlaneConversion(consumerHyperplane: Hyperplane, pointList, storyVectorList):

    my_prob = cplex.Cplex()
    my_prob.objective.set_sense(my_prob.objective.sense.maximize)

    my_obj = (len(storyVectorList)) * [0] # Not maximizing anything. No objective function.

    my_upperbound = len(storyVectorList) * [1]
    # my_upperbound.append(cplex.infinity)  # For variable Alpha.

    my_lowerbound = len(storyVectorList) * [0]
    # my_lowerbound.append(-cplex.infinity) # For Variable Alpha.

    my_colnames = ["a" + str(j) for j in range(len(storyVectorList))]
    # my_colnames.append("alpha")

    my_prob.variables.add(obj=my_obj, ub=my_upperbound, lb=my_lowerbound, names=my_colnames)

    my_rownames = ["r" + str(i) for i in range(2 * len(pointList) + 1)]
    my_sense = len(pointList) * "GL"
    my_sense = my_sense + "L"  # Sense for Sum(aj) <= k
    my_rows = []
    my_rhs = []

    for i in range(len(pointList)):
        #Changed the M to a very large number.
        rhs = [(ci - M * (1 - consumerHyperplane.pointSubscription[i])), (ci - e + M *
                                                                          consumerHyperplane.pointSubscription[i])]
        my_rhs += rhs

        rowParameter = []

        for j in range(len(storyVectorList)):
            n = [pointList[i][l] * storyVectorList[j][l] for l in range(len(pointList[i]))]
            rowParameter.append(1 / k * sum(n))
        # rowParameter.append(1)  # Parameter for Alpha.
        my_rows += 2 * [ [my_colnames, rowParameter] ]

    my_rows.append([my_colnames, len(storyVectorList)*[1]]) #sum(aj) <= k
    my_rhs.append(k)

    print(my_rows)
    print(my_rhs)
    print(my_sense)
    print(my_colnames)
    print(my_rownames)
    sys.stdout.flush()

    my_prob.linear_constraints.add(lin_expr=my_rows, senses=my_sense, rhs=my_rhs, names=my_rownames)
    #for i in range(len(my_colnames)):
    #    my_prob.variables.set_types( i , my_prob.variables.type.binary)

    my_prob.write("/Users/sly/Downloads/FakeNewsOutput/file.lp")

    my_prob.solve()

    if my_prob.solution.get_status() is not 1:
        raise CplexSolverError("No Solution exists.")
    print(my_prob.get_stats())

    numcols = my_prob.variables.get_num()
    x = my_prob.solution.get_values()
    isAllZeros = True
    for j in range(numcols):
        print("Column %s %d:  Value = %10f" %(my_colnames[j], j, x[j]))
        if x[j] != 0:
            isAllZeros = False
    if isAllZeros:
        print("Outputs all zeros. Error. No solution exists.")
        raise CplexSolverError("Outputs all zeros. Error. No solution exists.")

    endpoint = [0,0]
    for j in range(numcols): #Ignored alpha
        temp = [x[j] * storyVectorList[j][l] for l in range(len(storyVectorList[j]))]
        temp = [temp[l] / k for l in range(len(temp))]
        endpoint = [l+p for l,p in zip(temp, endpoint)]
    print("Endpoint is: " + str(endpoint))

    # generatedHyperplane = getHyperplaneEquation([endpoint, len(pointList[0])*[-0.001]])
    generatedHyperplane = Hyperplane(endpoint+[0], []) #ignored alpha. Alpha becommes 0.

    getHyperplaneListWithUtilities([generatedHyperplane], pointList, getMeanHyperplane(pointList).hyperPlaneEquation,
                                    storyVectorList, ci)
    print(generatedHyperplane.hyperPlaneEquation)
    print("Generated Hyperplane's points subscription:" + str(generatedHyperplane.pointSubscription) + "\n\n\n\n")

    return generatedHyperplane


def testHyperPlaneConversion():
    pointList = [[1, 1.1], [1,3], [3,1], [4,4]]
    storyVectorList = [[1, 1.1], [1,2], [2,1], [4,4.1]]
    hyperplane = getHyperplaneEquation([[1,2],[4, 4]])
    hyperplaneList = [hyperplane]

    getHyperplaneListWithUtilities(hyperplaneList,pointList, getMeanHyperplane(pointList).hyperPlaneEquation,
                                   storyVectorList, ci)

    print(hyperplane.hyperPlaneEquation)
    print(hyperplaneList[0].pointSubscription)
    try:
        convertedHyperplane = hyperPlaneConversion(hyperplane, pointList, storyVectorList)
    except CplexSolverError:
        print("Failed to generate.")

# testHyperPlaneConversion()
