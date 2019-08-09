import cplex
import sys
from DataStructure import *
from Multi_Dimension import *
from cplex.exceptions.errors import *

k = 3
ci = 2

e = 0.001
M = 10000

def hyperPlaneConversion(consumerHyperplane: Hyperplane, vList, xList):

    my_prob = cplex.Cplex()
    my_prob.objective.set_sense(my_prob.objective.sense.maximize)

    my_obj = (len(xList)) * [0] # Not maximizing anything. No objective function.

    my_upperbound = len(xList) * [1]
    # my_upperbound.append(cplex.infinity)  # For variable Alpha.

    my_lowerbound = len(xList) * [0]
    # my_lowerbound.append(-cplex.infinity) # For Variable Alpha.

    my_colnames = ["a" + str(j) for j in range(len(xList))]
    # my_colnames.append("alpha")

    my_prob.variables.add(obj=my_obj, ub=my_upperbound, lb=my_lowerbound, names=my_colnames)

    my_rownames = ["r" + str(i) for i in range(2 * len(vList) + 1)]
    my_sense = len(vList) * "GL"
    my_sense = my_sense + "L"  # Sense for Sum(aj) <= k

    my_rows = []
    my_rhs = []

    for i in range(len(vList)):
        #Changed the M to a very large number.
        rhs = [(ci - M * (1 - consumerHyperplane.pointSubscription[i])), (ci - e + M *
                                                                          consumerHyperplane.pointSubscription[i])]
        my_rhs += rhs

        rowParameter = []

        for j in range(len(xList)):
            n = [vList[i][l] * xList[j][l] for l in range(len(vList[i]))]
            rowParameter.append(1 / k * sum(n))#coefficient of a_j
        # rowParameter.append(1)  # Parameter for Alpha.
        my_rows += 2 * [ [my_colnames, rowParameter] ]

    my_rows.append([my_colnames, len(xList) * [1]]) #sum(aj) <= k
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

    print("The CPLEX status output is: " + str(my_prob.solution.get_status()))

    generatedHyperplane = []
    if my_prob.solution.get_status() is 1:
        a = my_prob.solution.get_values()
        for j in range(len(xList)):
            print("Column %s %d:  Value = %10f" % (my_colnames[j], j, xList[j]))

        generatedhyperplaneDirection = len(vList[0]) * [0]
        for j in range(len(xList)):
            temp = [a[j] * xList[j][l] for l in range(len(xList[j]))]#a_jx_j
            temp = [temp[l] / k for l in range(len(temp))]##(a_jx_j)/k
            generatedhyperplaneDirection = [l+p for l,p in zip(temp, generatedhyperplaneDirection)]
        print("Generated hyperplane direction is: " + str(generatedhyperplaneDirection))

        generatedHyperplane = Hyperplane(generatedhyperplaneDirection+[0], []) #ignored alpha. Alpha becommes 0.

        getHyperplaneListWithUtilities([generatedHyperplane], vList, getMeanHyperplane(vList).hyperPlaneEquation,
                                       xList, ci)
        if generatedHyperplane.pointSubscription != consumerHyperplane.pointSubscription:
            raise ValueError("Error in hyperplane conversion code. CPLEX returned a_j values without error, but still the m_i "
                  "values do not match")
        #print(generatedHyperplane.hyperPlaneEquation)
        #print("Generated Hyperplane's points subscription:" + str(generatedHyperplane.pointSubscription) + "\n\n\n\n")
    else:
        raise CplexSolverError("No Solution Exists. Cplex solution status not equals to " + str(my_prob.solution.get_status()))
    return generatedHyperplane


def testHyperPlaneConversion():
    pointList = [[1, 1.1], [1,3], [3,1], [4,4]]
    storyVectorList = [[1, 1.1], [1,2], [2,1], [4,4.1]]
    hyperplane = getHyperplaneEquation([[1,1.1],[4, 4]])
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
