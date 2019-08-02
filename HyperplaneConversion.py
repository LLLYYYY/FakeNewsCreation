import cplex
import sys
from DataStructure import *
from Multi_Dimension import *

k = 4
e = 0.1
ci = 1



def hyperPlaneConversion(consumerHyperplane: Hyperplane, pointList, storyVectorList):

    my_prob = cplex.Cplex()
    my_prob.objective.set_sense(my_prob.objective.sense.maximize)

    my_obj = (len(storyVectorList)+1) * [0] # Not maximizing anything. No objective function.

    my_upperbound = len(storyVectorList) * [1]
    my_upperbound.append(cplex.infinity)  # For variable Alpha.

    my_lowerbound = len(storyVectorList) * [-1]
    my_lowerbound.append(-cplex.infinity) # For Variable Alpha.

    my_colnames = ["a" + str(j) for j in range(len(storyVectorList))]
    my_colnames.append("alpha")


    my_prob.variables.add(obj=my_obj, ub=my_upperbound, names=my_colnames)

    my_rownames = ["r" + str(i) for i in range(2 * len(pointList) + 1)]
    my_sense = len(pointList) * "GL"
    my_sense = my_sense + "L"  # Sense for Sum(aj) <= k
    my_rows = []
    my_rhs = []

    for i in range(len(pointList)):

        rhs = [(ci - consumerHyperplane.M * (1 - consumerHyperplane.pointSubscription[i])), (ci - e +
                                                                                             consumerHyperplane.M *
                                                                                             consumerHyperplane.pointSubscription[i])]
        my_rhs += rhs

        rowParameter = []

        for j in range(len(storyVectorList)):
            n = [pointList[i][l] * storyVectorList[j][l] for l in range(len(pointList[i]))]
            rowParameter.append(1 / k * sum(n))
        rowParameter.append(1)  # Parameter for Alpha.
        my_rows += 2 * [ [my_colnames, rowParameter] ]



    my_rows.append([my_colnames[:-1], len(storyVectorList)*[1]]) #sum(aj) <= k
    my_rhs.append(k)

    print(my_rows)
    print(my_rhs)
    print(my_sense)
    print(my_colnames)
    print(my_rownames)
    sys.stdout.flush()

    my_prob.linear_constraints.add(lin_expr=my_rows, senses=my_sense, rhs=my_rhs, names=my_rownames)

    my_prob.solve()
    numcols = my_prob.variables.get_num()
    x = my_prob.solution.get_values()
    for j in range(numcols):
        print("Column %d:  Value = %10f" %(j, x[j]))


    endpoint = [0,0]
    for j in range(numcols - 1):
        temp = [x[j] * storyVectorList[j][l] for l in range(len(storyVectorList[j]))]
        temp = [temp[l] / k for l in range(len(temp))]
        endpoint = [l+p for l,p in zip(temp,endpoint)]
    print("Endpoint is: " + str(endpoint))

    # generatedHyperplane = getHyperplaneEquation([endpoint, len(pointList[0])*[-0.001]])
    #TODO: Add points that can plot the generated hyperplane.
    generatedHyperplane = Hyperplane(endpoint+[x[numcols-1]], [])

    getHyperplaneListWithUtilities([generatedHyperplane], pointList, getMeanHyperplane(pointList).hyperPlaneEquation,
                                    storyVectorList, ci)
    print(generatedHyperplane.hyperPlaneEquation)
    print("Generated Hyperplane's points subscription:" + str(generatedHyperplane.pointSubscription))

    return generatedHyperplane


def testHyperPlaneConversion():
    pointList = [[1,1], [1,3], [3,1], [4,4.1]]
    storyVectorList = [[1,1], [1,2], [2,1], [4,4.1]]
    hyperplane = getHyperplaneEquation([[2,1],[4, 4.1]])
    hyperplaneList = [hyperplane]

    getHyperplaneListWithUtilities(hyperplaneList,pointList, getMeanHyperplane(pointList).hyperPlaneEquation,
                                   storyVectorList, ci)

    print(hyperplane.hyperPlaneEquation)
    print(hyperplaneList[0].pointSubscription)

    hyperPlaneConversion(hyperplaneList[0], pointList, storyVectorList)

testHyperPlaneConversion()
