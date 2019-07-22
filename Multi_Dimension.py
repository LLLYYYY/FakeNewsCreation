import math
import numpy as np
from DataStructure import *

def getMeanStoryPoint(inputStoryVectorList):
    """Input story vector list, return unbiased mean line.
        This function is dimension free.
    """
    if not inputStoryVectorList:
        raise ValueError("The inputPointList is empty. Please check the input point list.")

    meanVector = []
    for i in range(len(inputStoryVectorList[0])):
        n = 0
        for line in inputStoryVectorList:
            n += line[i]
        n /= len(inputStoryVectorList)
        meanVector.append(n)

    return meanVector

def getHyperplaneEquation(pointList):
    """Input the point that require to form ONE hyperplane. Return the hyperplane equation.
        Dimension Free.
    """
    for i in range(len(pointList)):
        for j in range(i+1, len(pointList)):
            if pointList[i] == pointList[j]:
                raise ValueError("There are two same points in the point list. Failed to form a hyperplane.\n" +
                                 "PointA is " + str(pointList[i]) + " and pointB is " + str(pointList[j])+".")

    dimension = len(pointList[0])
    b = np.ones(dimension)
    pointMatrix = np.array(pointList)
    hyperplaneMatrix = np.linalg.solve(pointMatrix,b)
    hyperplaneEauation = hyperplaneMatrix.tolist()
    hyperplaneEauation.append(-1)


    if hyperplaneEauation[1] < 0:
        hyperplaneEauation = [-x for x in hyperplaneEauation]


    outputHyperplaneEquation = HyperPlane(hyperPlaneEquation = hyperplaneEauation,
                                          pointList= pointList)
    return outputHyperplaneEquation

def getOrthogonalUnitVector(inputHyperplane:HyperPlane):
    orthogonalVector = inputHyperplane.hyperPlaneEquation[:-1]
    meg = math.sqrt(sum([x**2 for x in orthogonalVector]))

    meg = meg * 5 # For testing purpose

    orthogonalUnitVector = [ x/meg for x in orthogonalVector]
    if orthogonalUnitVector[1] < 0:  #Just in case. Not gonna happen.
        orthogonalUnitVector = [-x for x in orthogonalUnitVector]

    return orthogonalUnitVector

def getHyperplaneListWithUtilities(inputHyperPlaneList: [HyperPlane], inputPointList, unbiasedVector):

    """Return hyperPlane list with utilities.
        Dimension Free.
        InputHyperPlaneList is a HyperPlane instance. But UnbiasedVector is just a vector list.
    """

    for i in range(len(inputHyperPlaneList)):
        inputHyperPlaneList[i].maximumPointNumber, inputHyperPlaneList[i].upperPointNumber, inputHyperPlaneList[
            i].lowerPointNumber, inputHyperPlaneList[i].onLinePointNumber = countPointsOfHyperplane(
            inputHyperPlaneList[i], inputPointList)

        # L2 Norm:
        norm = 0
        for k in range(len(inputHyperPlaneList[i].hyperPlaneEquation)): # Don't count the constant variable?
            norm += (inputHyperPlaneList[i].hyperPlaneEquation[k]/inputHyperPlaneList[i].hyperPlaneEquation[1] -
            unbiasedVector[k]/unbiasedVector[1]) ** 2  # When calculating the norm, I keep the y parameter to be 1.
        norm = math.sqrt(norm)

        inputHyperPlaneList[i].l2Norm = norm


def movePoints(defenderHyperplane: HyperPlane, adversaryHyperplane:HyperPlane, inputPointList):
    """Try to move points so that the defender hyperplane can has more point counts than adversary hyperplane.
        If succeed, return True, finalMovedPointList, defenderMaximumPointNumber, adveraryMaximumPointNumber
        If failed, return False, [empty list], defenderMaximumPointNumber, adveraryMaximumPointNumber
    """
    movedDefenderPointsList = []
    finalMovedPointList = []
    maximumDefenderPoints = defenderHyperplane.maximumPointNumber
    maximumAdversaryPoints = adversaryHyperplane.maximumPointNumber
    isSucceed = False

    if defenderHyperplane.maximumPointNumber == defenderHyperplane.upperPointNumber + defenderHyperplane.onLinePointNumber: # Upper has more
        for point in inputPointList:

            n = 0
            dimension = len(point)
            b = 0 # Use for calculating point to hyperplane distance.
            for i in range(dimension):
                n += point[i] * defenderHyperplane.hyperPlaneEquation[i]
                b += defenderHyperplane.hyperPlaneEquation[i] ** 2

            n += defenderHyperplane.hyperPlaneEquation[dimension]
            distance = (abs(n))/math.sqrt(b)

            if n < 0  and  distance <= 0.2:
                # Defender strategy. Upper has more. Move lower points to upper place.
                movedPoint = [x + y for x, y in zip(point, getOrthogonalUnitVector(defenderHyperplane))]
                # print(movedPoint)
                movedDefenderPointsList.append(movedPoint)
            else:
                movedDefenderPointsList.append(point)
    # elif inputLineWithUtilities[1][0] == inputLineWithUtilities[1][2] + inputLineWithUtilities[1][3]: # Lower has more
    else:  # Lower has more. Move Upper points to Lower place.
        for point in inputPointList:
            n = 0
            dimension = len(point)
            b = 0  # Use for calculating point to hyperplane distance.
            for i in range(dimension):
                n += point[i] * defenderHyperplane.hyperPlaneEquation[i]
                b += defenderHyperplane.hyperPlaneEquation[i] ** 2

            n += defenderHyperplane.hyperPlaneEquation[dimension]
            distance = (abs(n)) / math.sqrt(b)

            if n > 0 and distance <= 0.2:
                # Defender strategy. Lower has more. Move upper points to lower place.
                movedPoint = [x - y for x, y in
                              zip(point, getOrthogonalUnitVector(defenderHyperplane))]
                # print(movedPoint)
                movedDefenderPointsList.append(movedPoint)
            else:
                movedDefenderPointsList.append(point)
    # else:  # If two side has the same number of points. Haven't implemented.
    #     raise ValueError("Crash at movedPointList")
    #     ##########################Haven't implemented!!!!!!!!!!!!!!!!!!

    if adversaryHyperplane.maximumPointNumber == adversaryHyperplane.upperPointNumber + \
            adversaryHyperplane.onLinePointNumber: # Upper has more
        for point in movedDefenderPointsList:

            n = 0
            dimension = len(point)
            b = 0 # Use for calculating point to hyperplane distance.
            for i in range(dimension):
                n += point[i] * adversaryHyperplane.hyperPlaneEquation[i]
                b += adversaryHyperplane.hyperPlaneEquation[i] ** 2

            n += adversaryHyperplane.hyperPlaneEquation[dimension]
            distance = (abs(n))/math.sqrt(b)

            if n < 0  and  distance <= 0.2:
                # Adversary strategy. Upper has more. Move upper points to lower place.
                movedPoint = [x + (-y) for x, y in zip(point, getOrthogonalUnitVector(
                    adversaryHyperplane))]
                if isTwoPointsOnTheSameSideOfHyperplane(movedPoint, point, defenderHyperplane): #Check if moved points hurts defender
                    # utility.
                    finalMovedPointList.append(movedPoint)
                else:
                    finalMovedPointList.append(point)
            else:
                finalMovedPointList.append(point)
    # elif inputLineWithUtilities[1][0] == inputLineWithUtilities[1][2] + inputLineWithUtilities[1][3]: # Lower has more
    else:  # Lower has more. Move Upper points to Lower place.
        for point in movedDefenderPointsList:
            n = 0
            dimension = len(point)
            b = 0  # Use for calculating point to hyperplane distance.
            for i in range(dimension):
                n += point[i] * adversaryHyperplane.hyperPlaneEquation[i]
                b += adversaryHyperplane.hyperPlaneEquation[i] ** 2

            n += adversaryHyperplane.hyperPlaneEquation[dimension]
            distance = (abs(n)) / math.sqrt(b)

            if n > 0 and distance <= 0.2:
                # Adversary strategy. Lower has more. Move lower points to upper place.
                movedPoint = [x - (-y) for x, y in
                              zip(point, getOrthogonalUnitVector(adversaryHyperplane))]
                if isTwoPointsOnTheSameSideOfHyperplane(movedPoint, point, defenderHyperplane):  #Check if moved points hurts defender
                    # utility.
                    finalMovedPointList.append(movedPoint)
                else:
                    finalMovedPointList.append(point)
            else:
                finalMovedPointList.append(point)
    # else:  # If two side has the same number of points. Haven't implemented.
    #     raise ValueError("Crash at movedPointList")
    #     ##########################Haven't implemented!!!!!!!!!!!!!!!!!!

    # print(movedPointsList)
    defenderMaximumPoints, _, _, _ = countPointsOfHyperplane(defenderHyperplane, finalMovedPointList)
    adversarymaximumPionts, _,_,_ = countPointsOfHyperplane(adversaryHyperplane, finalMovedPointList)

    if defenderMaximumPoints >= adversarymaximumPionts:
        return True, finalMovedPointList, defenderMaximumPoints, adversarymaximumPionts
    else:
        return False, [], defenderMaximumPoints, adversarymaximumPionts


def isTwoPointsOnTheSameSideOfHyperplane(pointA, pointB, hyperplane:HyperPlane):
    isUpperA = 0
    isUpperB = 0

    m = 0
    n = 0
    dimension = len(pointA)
    for i in range(dimension):
        m += pointA[i] * hyperplane.hyperPlaneEquation[i]
        n += pointB[i] * hyperplane.hyperPlaneEquation[i]
    m += hyperplane.hyperPlaneEquation[dimension]
    n += hyperplane.hyperPlaneEquation[dimension]

    if m > 0:
        if n < 0:
            return False
        else:
            return True
    elif m < 0:
        if n > 0:
            return False
        else:
            return True
    else:
        return True

def countPointsOfHyperplane(inputHyperPlane:HyperPlane, inputPointList):
    maximumPointNumber = 0
    upperPointNumber = 0
    lowerPointNumber = 0
    onLinePointNumber = 0
    for i in range(len(inputPointList)):
        dimension = len(inputPointList[0])
        n = 0
        for j in range(dimension):
            n += inputHyperPlane.hyperPlaneEquation[j] * inputPointList[i][j]
        n += inputHyperPlane.hyperPlaneEquation[dimension]  # Constant variables b.
        if n > 0:
            upperPointNumber += 1
        elif n < 0:
            lowerPointNumber += 1
        else:
            onLinePointNumber += 1

    if upperPointNumber > lowerPointNumber:
        maximumPointNumber = upperPointNumber + onLinePointNumber
    else:  # include upper == lower
        maximumPointNumber = lowerPointNumber + onLinePointNumber

    return maximumPointNumber, upperPointNumber, lowerPointNumber, onLinePointNumber


### Test

def testGetHyperplaneEquation():
    inputPoints = [[4, 0, -1, 0], [1, 2, 3, -1], [0, -1, 2, 0], [-1, 1, -1, 1]]
    outputHyperPlane = getHyperplaneEquation(inputPoints)
    if outputHyperPlane.hyperPlaneEquation != [0.40625, 0.25, 0.625, 1.7812500000000002, -1]:
        raise ValueError("hyperPlane Calculation ERROR!\n" +
                         "Calculated hyperPlane is " + str(outputHyperPlane.hyperPlaneEquation) + ". Correct hyperplane should be: [[["
                                                                                "0.40625, 0.25, 0.625, 1.7812500000000002, -1]],[[4, 0, -1, 0], [1, 2, 3, -1], [0, -1, 2, 0], [-1, 1, -1, 1]]]:")

    inputPoints = [[3,2],[2,3]]
    outputHyperPlane = getHyperplaneEquation(inputPoints)
    print(outputHyperPlane.hyperPlaneEquation)
    outputUnitNormalVector = getOrthogonalUnitVector(outputHyperPlane)
    print(outputUnitNormalVector)

def testGetHyperplaneListWithUtilities():
    hyperPlaneA = HyperPlane([1,1,-5], [[0,5],[5,0]])
    hyperPlaneB = HyperPlane([1, 2, -5], [[0, 2.5], [5, 0]])
    hyperPlaneList = [hyperPlaneA,hyperPlaneB]
    unbiasedPlane = [1,1,-5]
    pointList = [[1,1],[2,2],[3,3],[4,4],[5,5]]
    getHyperplaneListWithUtilities(hyperPlaneList, pointList, unbiasedPlane)
    print(hyperPlaneList[1].maximumPointNumber)

# testGetHyperplaneEquation()
# testGetHyperplaneListWithUtilities()