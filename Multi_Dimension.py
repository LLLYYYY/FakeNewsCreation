import math
import numpy as np
from DataStructure import *

longestMovingDistance = 0.4

def getMeanHyperplane(inputStoryVectorList):
    """Input story vector list, return unbiased mean line.
        This function is dimension free.
    """
    if not inputStoryVectorList:
        raise ValueError("The inputPointList is empty. Please check the input point list.")

    meanPoint = []
    for i in range(len(inputStoryVectorList[0])):
        n = 0
        for line in inputStoryVectorList:
            n += line[i]
        n /= len(inputStoryVectorList)
        meanPoint.append(n)

    meanHyperplane = Hyperplane([*meanPoint, 0], [meanPoint, [-0.0001, -0.0001]])
    return meanHyperplane

#TODO: HANDLE PARALLEL VECTORS IN HIGHER DIMENSIONS
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

    if hyperplaneEauation[1] == 0:
        raise ValueError("Hyperplane parallel to the y axis. Error!")
    else:
        devider = hyperplaneEauation[1]
        hyperplaneEauation = [x/devider for x in hyperplaneEauation]

    outputHyperplaneEquation = Hyperplane(hyperPlaneEquation = hyperplaneEauation,
                                          pointList= pointList)
    return outputHyperplaneEquation

def getOrthogonalUnitVector(inputHyperplane:Hyperplane):
    orthogonalVector = inputHyperplane.hyperPlaneEquation[:-1]
    meg = math.sqrt(sum([x**2 for x in orthogonalVector]))

    orthogonalUnitVector = [ x/meg for x in orthogonalVector]
    if orthogonalUnitVector[1] < 0:  #Just in case. Not gonna happen.
        orthogonalUnitVector = [-x for x in orthogonalUnitVector]

    return orthogonalUnitVector


def getHyperplaneListWithUtilities(inputHyperPlaneList: [Hyperplane], inputPointList, unbiasedVector, inputStoryVector, ci):

    """Return hyperPlane list with utilities.
        Dimension Free.
        InputHyperPlaneList is a Hyperplane instance. But UnbiasedVector is just a vector list.
    """

    for i in range(len(inputHyperPlaneList)):
        inputHyperPlaneList[i].maximumPointNumber, \
        inputHyperPlaneList[
            i].upperPointNumber, inputHyperPlaneList[i].lowerPointNumber, inputHyperPlaneList[i].onLinePointNumber, \
        inputHyperPlaneList[i].pointSubscription, inputHyperPlaneList[i].M = \
            countPointsOfHyperplane(
            inputHyperPlaneList[i], inputPointList,  ci)

        # L2 Norm:
        norm = 0
        for k in range(len(inputHyperPlaneList[i].hyperPlaneEquation)-1): # Don't count the constant variable???  Not
            # counting now.
            #TODO: It is possible that hyperplaneequation[1] == 0. It will crush.
            norm += (inputHyperPlaneList[i].hyperPlaneEquation[k]/inputHyperPlaneList[i].hyperPlaneEquation[1] -
            unbiasedVector[k]/unbiasedVector[1]) ** 2  # When calculating the norm, I keep the y parameter to be 1.
        norm = math.sqrt(norm)

        inputHyperPlaneList[i].l2Norm = norm

def twoPointsDistance (pointA, pointB):
    dimension = len(pointA)
    distance = 0
    for i in range(dimension):
        distance += ( pointB[i] - pointA[i]) * ( pointB[i] - pointA[i])
    distance = math.sqrt(distance)
    return distance




def movePoints(defenderHyperplane: Hyperplane, adversaryHyperplane:Hyperplane, inputPointList, oringinalPointList, ci):
    """Try to move points so that the defender hyperplane can has more point counts than adversary hyperplane.
        If succeed, return True, finalMovedPointList, defenderMaximumPointNumber, adveraryMaximumPointNumber
        If failed, return False, [empty list], defenderMaximumPointNumber, adveraryMaximumPointNumber
    """
    movedDefenderPointsList = []
    finalMovedPointList = []

    if defenderHyperplane.maximumPointNumber == defenderHyperplane.upperPointNumber + defenderHyperplane.onLinePointNumber: # Upper has more
        for i in range(len(inputPointList)):

            n = 0
            dimension = len(inputPointList[i])
            b = 0 # Use for calculating point to hyperplane distance.
            for j in range(dimension):
                n += inputPointList[i][j] * defenderHyperplane.hyperPlaneEquation[j]
                b += defenderHyperplane.hyperPlaneEquation[j] ** 2

            n += defenderHyperplane.hyperPlaneEquation[dimension]
            distance = (abs(n))/math.sqrt(b)

            if n < 0  and  distance <= 0.2:
                # Defender strategy. Upper has more. Move lower points to upper place.
                movedPoint1 = [x + y for x, y in zip(inputPointList[i], [0.2 * z for z in getOrthogonalUnitVector(
                    defenderHyperplane)])]
                distanceToOriginalPoints1 = twoPointsDistance(oringinalPointList[i], movedPoint1)
                movedPoint2 = [x + y for x, y in zip(inputPointList[i], [distance * z for z in getOrthogonalUnitVector(
                    defenderHyperplane)])]
                distanceToOriginalPoints2 = twoPointsDistance(oringinalPointList[i], movedPoint2)
                if distanceToOriginalPoints1 <= longestMovingDistance:
                    movedDefenderPointsList.append(movedPoint1)
                elif distanceToOriginalPoints2 <= longestMovingDistance:
                    movedDefenderPointsList.append(movedPoint2)
                else:
                    movedDefenderPointsList.append(inputPointList[i])
            else:
                movedDefenderPointsList.append(inputPointList[i])
    # elif inputLineWithUtilities[1][0] == inputLineWithUtilities[1][2] + inputLineWithUtilities[1][3]: # Lower has more
    else:  # Lower has more. Move Upper points to Lower place.
        for i in range(len(inputPointList)):
            n = 0
            dimension = len(inputPointList[i])
            b = 0  # Use for calculating point to hyperplane distance.
            for j in range(dimension):
                n += inputPointList[i][j] * defenderHyperplane.hyperPlaneEquation[j]
                b += defenderHyperplane.hyperPlaneEquation[j] ** 2

            n += defenderHyperplane.hyperPlaneEquation[dimension]
            distance = (abs(n)) / math.sqrt(b)

            if n > 0 and distance <= 0.2:
                # Defender strategy. Lower has more. Move upper points to lower place.
                movedPoint1 = [x - y for x, y in
                              zip(inputPointList[i], [0.2 * x for x in getOrthogonalUnitVector(defenderHyperplane)])]
                distanceToOriginalPoints1 = twoPointsDistance(oringinalPointList[i], movedPoint1)
                movedPoint2 = [x - y for x, y in zip(inputPointList[i], [distance * x for x in getOrthogonalUnitVector(defenderHyperplane)])]
                distanceToOriginalPoints2 = twoPointsDistance(oringinalPointList[i], movedPoint2)
                if distanceToOriginalPoints1 <= longestMovingDistance:
                    movedDefenderPointsList.append(movedPoint1)
                elif distanceToOriginalPoints2 <= longestMovingDistance:
                    movedDefenderPointsList.append(movedPoint2)
                else:
                    movedDefenderPointsList.append(inputPointList[i])
            else:
                movedDefenderPointsList.append(inputPointList[i])
    # else:  # If two side has the same number of points. Haven't implemented.
    #     raise ValueError("Crash at movedPointList")
    #     ##########################Haven't implemented!!!!!!!!!!!!!!!!!!


    # #Problems with this algorithm. Check back later!!!
    # # Move points to hurt the adversary.
    # if adversaryHyperplane.maximumPointNumber == adversaryHyperplane.upperPointNumber + \
    #         adversaryHyperplane.onLinePointNumber: # Upper has more
    #     for point in movedDefenderPointsList:
    #
    #         n = 0
    #         dimension = len(point)
    #         b = 0 # Use for calculating point to hyperplane distance.
    #         for i in range(dimension):
    #             n += point[i] * adversaryHyperplane.hyperPlaneEquation[i]
    #             b += adversaryHyperplane.hyperPlaneEquation[i] ** 2
    #
    #         n += adversaryHyperplane.hyperPlaneEquation[dimension]
    #         distance = (abs(n))/math.sqrt(b)
    #
    #         if n > 0  and  distance <= 0.2:
    #             # Adversary strategy. Upper has more. Move upper points to lower place.
    #             movedPoint = [x - y for x, y in zip(point, getOrthogonalUnitVector(
    #                 adversaryHyperplane))]
    #             if isTwoPointsOnTheSameSideOfHyperplane(movedPoint, point, defenderHyperplane): #Check if moved points hurts defender
    #                 # utility.
    #                 finalMovedPointList.append(movedPoint)
    #             else:
    #                 finalMovedPointList.append(point)
    #         else:
    #             finalMovedPointList.append(point)
    # # elif inputLineWithUtilities[1][0] == inputLineWithUtilities[1][2] + inputLineWithUtilities[1][3]: # Lower has more
    # else:  # Lower has more. Move Upper points to Lower place.
    #     for point in movedDefenderPointsList:
    #         n = 0
    #         dimension = len(point)
    #         b = 0  # Use for calculating point to hyperplane distance.
    #         for i in range(dimension):
    #             n += point[i] * adversaryHyperplane.hyperPlaneEquation[i]
    #             b += adversaryHyperplane.hyperPlaneEquation[i] ** 2
    #
    #         n += adversaryHyperplane.hyperPlaneEquation[dimension]
    #         distance = (abs(n)) / math.sqrt(b)
    #
    #         if n < 0 and distance <= 0.2:
    #             # Adversary strategy. Lower has more. Move lower points to upper place.
    #             movedPoint = [x + y for x, y in
    #                           zip(point, getOrthogonalUnitVector(adversaryHyperplane))]
    #             if isTwoPointsOnTheSameSideOfHyperplane(movedPoint, point, defenderHyperplane):  #Check if moved points hurts defender
    #                 # utility.
    #                 finalMovedPointList.append(movedPoint)
    #             else:
    #                 finalMovedPointList.append(point)
    #         else:
    #             finalMovedPointList.append(point)
    # # else:  # If two side has the same number of points. Haven't implemented.
    # #     raise ValueError("Crash at movedPointList")
    # #     ##########################Haven't implemented!!!!!!!!!!!!!!!!!!
    finalMovedPointList = movedDefenderPointsList
    # print(movedPointsList)
    defenderMaximumPoints, _, _, _ , _, _ = countPointsOfHyperplane(defenderHyperplane, finalMovedPointList,
                                                             ci= ci)
    adversarymaximumPoints, _, _, _ , _, _ = countPointsOfHyperplane(adversaryHyperplane, finalMovedPointList, ci = ci)

    if defenderMaximumPoints >= adversarymaximumPoints and defenderMaximumPoints > 0:
        return True, finalMovedPointList, defenderMaximumPoints, adversarymaximumPoints
    elif defenderMaximumPoints == 0:
        raise Exception("Moved points failure. Bug!")
    else:
        return False, [], defenderMaximumPoints, adversarymaximumPoints


def isTwoPointsOnTheSameSideOfHyperplane(pointA, pointB, hyperplane:Hyperplane):

    m = 0
    n = 0
    dimension = len(pointA)
    for i in range(dimension):
        m += pointA[i] * hyperplane.hyperPlaneEquation[i]
        n += pointB[i] * hyperplane.hyperPlaneEquation[i]
    m += hyperplane.hyperPlaneEquation[dimension]
    n += hyperplane.hyperPlaneEquation[dimension]

    if m * n < 0:
        return False
    else:
        # print("Point Moved.")
        return True

def countPointsOfHyperplane(inputHyperplane:Hyperplane, inputPointList, ci):
    pointSubscribedList = []
    maximumPointNumber = 0
    upperPointNumber = 0
    lowerPointNumber = 0
    onLinePointNumber = 0
    M = 0
    for i in range(len(inputPointList)):
        dimension = len(inputPointList[0])
        n = 0
        for j in range(dimension):
            n += inputHyperplane.hyperPlaneEquation[j] * inputPointList[i][j]
        n += inputHyperplane.hyperPlaneEquation[dimension]  # Constant variables b.
        # if inputPointList[i] == inputHyperplane.pointList[0]:
        #     upperPointNumber += 1
        # elif inputPointList[i] == inputHyperplane.pointList[1]:  # At least two points
        #     lowerPointNumber += 1
        # elif n > 0:
        if n > 0:  #TODO: Behavior unknown.
            upperPointNumber += 1
        elif n < 0:
            lowerPointNumber += 1
        else:
            onLinePointNumber += 1

    if upperPointNumber > lowerPointNumber:
        maximumPointNumber = upperPointNumber + onLinePointNumber
    else:  # include upper == lower
        maximumPointNumber = lowerPointNumber + onLinePointNumber

    for inputPoint in inputPointList:
        pointSubscribed = 0
        n = []
        for j in range(len(inputPoint)):
            n.append(inputHyperplane.hyperPlaneEquation[j] * inputPoint[j])
        n.append(inputHyperplane.hyperPlaneEquation[-1])  # Re-enable the constant variable.
        n = sum(n)
        if n >= ci:
            pointSubscribed = 1
            M += 1
            # print("News Subscribed, point" + str(inputPoint) + " Hyperplane:" + str(
            #     inputHyperplane.hyperPlaneEquation))
        else:
            pointSubscribed = 0
        pointSubscribedList.append(pointSubscribed)
    return maximumPointNumber, upperPointNumber, lowerPointNumber, onLinePointNumber, pointSubscribedList, M,

def newsSubscription(comsumerHyperplane:Hyperplane, inputPoint, ci):
    pointSubscribed = 0
    n = []
    for j in range(len(inputPoint)):
        n.append(comsumerHyperplane.hyperPlaneEquation[j] * inputPoint[j])
    n.append(comsumerHyperplane.hyperPlaneEquation[-1])
    n = sum(n)
    if n>= ci:
        pointSubscribed = 1
        print("News Subscribed, point" + str(inputPoint) + " Hyperplane:" + str(
            comsumerHyperplane.hyperPlaneEquation))
    else:
        pointSubscribed = 0
    return pointSubscribed

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
    hyperPlaneA = Hyperplane([1, 1, -5], [[0, 5], [5, 0]])
    hyperPlaneB = Hyperplane([1, 2, -5], [[0, 2.5], [5, 0]])
    hyperPlaneList = [hyperPlaneA,hyperPlaneB]
    unbiasedPlane = [1,1,-5]
    pointList = [[1,1],[2,2],[3,3],[4,4],[5,5]]
    getHyperplaneListWithUtilities(hyperPlaneList, pointList, unbiasedPlane)
    print(hyperPlaneList[1].maximumPointNumber)

# testGetHyperplaneEquation()
# testGetHyperplaneListWithUtilities()