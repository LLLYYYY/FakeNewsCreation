import cplex
import sys
from DataStructure import *
from Multi_Dimension import *

K = 10
e = 0.001
ci = 0


def hyperPlaneConversion(consumerHyperplane: Hyperplane, pointList, storyVector):

    my_prob = cplex.Cplex()
    my_prob.objective.set_sense(my_prob.objective.sense.maximize)

    my_obj = len(storyVector) * [0]
    my_upperbound = len(storyVector) * [1]
    my_colnames = ["a" + str(j) for j in range(len(storyVector))]
    #######
    my_colnames.append("a"+str(len(storyVector)))
    #######

    my_prob.variables.add(obj=my_obj, ub=my_upperbound, names=my_colnames)

    my_rownames = ["r" + str(i) for i in range(2 * len(pointList))]
    my_sense = len(pointList) * "GL"
    # my_sense = my_sense + "E"
    my_rows = []
    my_rhs = []

    #TODO: Should be pointlist...2 constraints fir each point, not each story
    for i in range(len(storyVector)):

        rhs = [( K * ci - consumerHyperplane.M * (1 - consumerHyperplane.pointScribed[i])),( K * ci - e +
                                                                                           consumerHyperplane.M *
               consumerHyperplane.pointScribed[i]) ]
        my_rhs += rhs

        rowParameter = []
        #TODO: Should be storyVector.
        for j in range(len(pointList)):
            n = [pointList[i][k] * storyVector[j][k] for k in range(len(pointList[i]))]
            rowParameter.append(sum(n))
        # rowParameter += [-ci]
        my_rows += 2 * [ [my_colnames, rowParameter] ]

        #TODO ADD real ALPHA, CONSTRAINT on a_j<k, and add lower bound on a_j

    # my_rows.append([my_colnames, len(storyVector)*[1] + [-1]])
    # my_rhs.append(0)

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


def testHyperPlaneConversion():
    pointList = [[1,1], [1,2], [2,1], [4,4.1]]
    storyVectorList = [[1,1], [1,3], [3,1], [4,4.1]]
    hyperplane = getHyperplaneEquation([[1,1],[4, 4.1]])
    hyperplaneList = [hyperplane]

    getHyperplaneListWithUtilities(hyperplaneList,pointList, getMeanHyperplane(pointList).hyperPlaneEquation,
                                   storyVectorList, ci)

    print(hyperplane.hyperPlaneEquation)
    print(hyperplaneList[0].pointScribed)

    hyperPlaneConversion(hyperplaneList[0], pointList, storyVectorList)

testHyperPlaneConversion()
