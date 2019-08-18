import cplex
import sys
from DataStructure import *
from Multi_Dimension import *
from cplex.exceptions.errors import *
import numpy as np

def hyperPlaneConversion(consumerHyperplane, vList, xList):

    my_prob = cplex.Cplex()

    my_prob.set_log_stream(None)
    my_prob.set_error_stream(None)
    my_prob.set_warning_stream(None)
    my_prob.set_results_stream(None)

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
        #Changed the adversaryUtility to a very large number.
        rhs = [(ci - M * (1 - consumerHyperplane.pointSubscription[i])), (ci - e + M *
                                                                          consumerHyperplane.pointSubscription[i])]
        my_rhs += rhs

        rowParameter = []

        for j in range(len(xList)):
            n = [vList[i][l] * xList[j][l] for l in range(len(vList[i]))]
            rowParameter.append(sum(n)/k)#coefficient of a_j
        # rowParameter.append(1)  # Parameter for Alpha.
        my_rows += [[my_colnames, rowParameter]]
        my_rows += [[my_colnames, rowParameter]]

    my_rows.append([my_colnames, len(xList) * [1]]) #sum(aj) <= k
    my_rhs.append(k)

    #print(my_rows)
    #print(my_rhs)
    #print(my_sense)
    #print(my_colnames)
    #print(my_rownames)
    #sys.stdout.flush()

    my_prob.linear_constraints.add(lin_expr=my_rows, senses=my_sense, rhs=my_rhs, names=my_rownames)
    #for i in range(len(my_colnames)):
    #    my_prob.variables.set_types( i , my_prob.variables.type.binary)

    # my_prob.write("/Users/sly/Downloads/FakeNewsOutput/file.lp")
    # my_prob.write("/Users/auy212-admin/Downloads/FakeNewsOutput/file.lp")
    try:
        my_prob.solve()
    except CplexSolverError:
        print("Failed to generated hyperplane.")
        return None

    # print("The CPLEX status output is: " + str(my_prob.solution.get_status()))

    if my_prob.solution.get_status() == 1:
        a = my_prob.solution.get_values()
        isAllZeros = True
        for j in range(len(xList)):
            #print("Column " + str(my_colnames[j]) + " " + str(j) + ", value = " + str(a[j]))
            if a[j] != 0.0:
                isAllZeros = False

        if isAllZeros is True:
            raise ValueError("CPLEX return all zeros solution.")

        generatedhyperplaneDirection = np.zeros(len(vList[0]))
        for j in range(len(xList)):
            temp = a[j] * xList[j] / k  #(a_j*x_j)/k
            generatedhyperplaneDirection += temp
        # print("Consumer hyperplane is: " + str(consumerHyperplane.hyperPlaneEquation))
        # print("Generated hyperplane is: " + str(generatedhyperplaneDirection) + str(-1*ci))

        convertedHyperplane = Hyperplane(np.append(generatedhyperplaneDirection,0), []) #ignored alpha. Alpha
        # becommes 0.

        # for point in vList:
        #     # print(point)
        #     debugsinglePointSubscribeOfHyperplane(convertedHyperplane, point, ci)

        #getOriginalHyperplaneListWithUtilities([convertedHyperplane], vList, getMeanHyperplane(vList).hyperPlaneEquation,xList, ci)
        # getOriginalHyperplaneListWithUtilities([convertedHyperplane], vList, getMeanHyperplane(vList).hyperPlaneEquation)
        # originalConvertedHyperplane = []
        # originalConvertedHyperplane.append([consumerHyperplane, convertedHyperplane])
        # generatedHyperplaneList = getConvertedHyperplaneListWithUtilities(originalConvertedHyperplane, vList,
        #                                                                   getMeanHyperplane(xList).hyperPlaneEquation,
        #                                                                   ci)
        # convertedHyperplane = generatedHyperplaneList[0]

        # print(consumerHyperplane.pointSubscription)
        # print(convertedHyperplane.pointSubscription)

        # if convertedHyperplane.pointSubscription != consumerHyperplane.pointSubscription:
        #     raise ValueError("Error in hyperplane conversion code. CPLEX returned a_j values without error, but still the m_i "
        #           "values do not match")
        #print(convertedHyperplane.hyperPlaneEquation)
        #print("Generated Hyperplane's points subscription:" + str(convertedHyperplane.pointSubscription) + "\n\n\n\n")
        return consumerHyperplane, convertedHyperplane
    else:
        # raise CplexSolverError("No Solution Exists. Cplex solution status equals to " + str(my_prob.solution.get_status()))
        # print("Failed to generated hyperplane.")
        return None

def testHyperPlaneConversion():
    pointList = [[1, 1], [-1,-2]]
    storyVectorList = [[1, 0], [0,1]]
    #TODO: Represents a hacky solution that will atleast work for 2d examples. Will need to think about N dimensions.
    hyperplane = getHyperplaneEquation([[1+e,1+e],[-1-e, -2-e]])
    hyperplaneList = [hyperplane]

    getOriginalHyperplaneListWithUtilities(hyperplaneList, pointList, getMeanHyperplane(pointList).hyperPlaneEquation)

    print(hyperplane.hyperPlaneEquation)
    print(hyperplaneList[0].pointSubscription)
    try:
        convertedHyperplane = hyperPlaneConversion(hyperplane, pointList, storyVectorList)
    except CplexSolverError:
        print("Failed to generate.")

    getOriginalHyperplaneListWithUtilities([convertedHyperplane], pointList, getMeanHyperplane(pointList).hyperPlaneEquation)

    if convertedHyperplane.pointSubscription != hyperplane.pointSubscription:
        raise ValueError(
            "Error in hyperplane conversion code. CPLEX returned a_j values without error, but still the m_i "
            "values do not match")

#testHyperPlaneConversion()
