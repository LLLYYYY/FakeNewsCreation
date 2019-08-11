import math
import numpy as np
from DataStructure import *
from config import *

def getMeanHyperplane(inputStoryVectorList):
    """Input story vector list, return unbiased mean line.
        This function is dimension free.
    """
    if not inputStoryVectorList:
        raise ValueError("The consumerPointList is empty. Please check the input point list.")

    meanPoint = []
    for i in range(len(inputStoryVectorList[0])):
        n = 0
        for line in inputStoryVectorList:
            n += line[i]
        n /= len(inputStoryVectorList)
        meanPoint.append(n)

    # # Change to unit vector.
    # meg = math.sqrt(sum([x**2 for x in meanPoint]))
    # if meg != 0:
    #     for i in range(len(meanPoint)):
    #         meanPoint[i] = meanPoint[i] / meg
    # else:
    #     raise ValueError("Getting a all zeros mean points")

    meanHyperplane = Hyperplane([*meanPoint, 0])
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

    # # When y = 0, possible to crash.
    # if hyperplaneEauation[1] < 0:
    #     hyperplaneEauation = [-x for x in hyperplaneEauation]
    #
    # if hyperplaneEauation[1] == 0:
    #     raise ValueError("Hyperplane parallel to the y axis. Error!")
    # else:
    #     devider = hyperplaneEauation[1]
    #     hyperplaneEauation = [x/devider for x in hyperplaneEauation]
    # meg = math.sqrt(sum([x ** 2 for x in hyperplaneEauation[-1]]))
    # for i in range(len(hyperplaneEauation)):
    #     hyperplaneEauation[i] = hyperplaneEauation[i] / meg

    outputHyperplaneEquation = Hyperplane(hyperPlaneEquation = hyperplaneEauation)
    return outputHyperplaneEquation

def getOrthogonalUnitVector(inputHyperplane:Hyperplane):
    orthogonalVector = inputHyperplane.hyperPlaneEquation[:-1]

    meg = math.sqrt(sum([x**2 for x in orthogonalVector]))
    orthogonalUnitVector = [ x/meg for x in orthogonalVector]

    return orthogonalUnitVector


def getOriginalHyperplaneListWithUtilities(inputHyperPlaneList: [Hyperplane], consumerPointList, unbiasedVector):

    """Return hyperPlane list with utilities.
        Dimension Free.
        InputHyperPlaneList is a Hyperplane instance. But UnbiasedVector is just a vector list.
    """

    for i in range(len(inputHyperPlaneList)):

        inputHyperPlaneList[i].pointSubscription, inputHyperPlaneList[i].adversaryUtility = \
            countSubscribersOfHyperplane(
            inputHyperPlaneList[i], consumerPointList, 0)

        # L2 Norm:
        norm = 0
        for k in range(len(inputHyperPlaneList[i].hyperPlaneEquation)-1): # Don't count the constant variable???  Not
            # counting now.
            norm += (inputHyperPlaneList[i].hyperPlaneEquation[k] -
            unbiasedVector[k]) ** 2  # When calculating the norm, I keep the y parameter to be 1.
        norm = math.sqrt(norm)

        inputHyperPlaneList[i].defenderUtility = norm
    return inputHyperPlaneList

def getConvertedHyperplaneListWithUtilities(originalConvertedHyperplaneMatchList: [[Hyperplane, Hyperplane]],
                                            consumerPointList, unbiasedVector, ci):
    """Dimension Free.
        Mostly the same as get original hyperplane utilities function. Added ci number and check subscription list.
    """
    originalHyperplaneList = [originalConvertedHyperplaneMatchList[i][0] for i in range(len(originalConvertedHyperplaneMatchList))]
    convertedHyperplaneList = [originalConvertedHyperplaneMatchList[i][1] for i in range(len(
        originalConvertedHyperplaneMatchList))]

    for i in range(len(convertedHyperplaneList)):
        convertedHyperplaneList[i].pointSubscription, convertedHyperplaneList[i].adversaryUtility = countSubscribersOfHyperplane(
            convertedHyperplaneList[i], consumerPointList,  ci)

        if convertedHyperplaneList[i].pointSubscription != originalHyperplaneList[i].pointSubscription:
            raise ValueError("The converted hyperplane has different point subscription compare to the original.")

        # L2 Norm:
        norm = 0
        for k in range(
                len(convertedHyperplaneList[i].hyperPlaneEquation) - 1):  # Don't count the constant variable???  Not
            # counting now.
            norm += (convertedHyperplaneList[i].hyperPlaneEquation[k] -
                     unbiasedVector[k]) ** 2  # When calculating the norm, I keep the y parameter to be 1.
        norm = math.sqrt(norm)
        convertedHyperplaneList[i].defenderUtility = norm
    return convertedHyperplaneList



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

    # Move points to benefits defender.
    # Always move upward.
    for i in range(len(inputPointList)):

        # Defender strategy. Always move upward.
        if defenderHyperplane.pointSubscription[i] == 0:
            movedPoint = [x + y for x, y in zip(inputPointList[i], [singleTimeMovingDistance * z for z in getOrthogonalUnitVector(
                defenderHyperplane)])]
            distanceToOriginalPoints = twoPointsDistance(oringinalPointList[i], movedPoint)

            if distanceToOriginalPoints <= longestMovingDistance and singlePointSubscribeOfHyperplane(
                    defenderHyperplane, movedPoint, ci) == 1:
                movedDefenderPointsList.append(movedPoint)
            else:
                movedDefenderPointsList.append(inputPointList[i]) # Not moving this point because the total moving
                # distance is too large or cannot change the subscription status.
        else:
            movedDefenderPointsList.append(inputPointList[i]) # This point is already subscribed.


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
    #             movedPoint = [xList - y for xList, y in zip(point, getOrthogonalUnitVector(
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
    #             movedPoint = [xList + y for xList, y in
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

    finalMovedPointList = movedDefenderPointsList # TODO: Delete this line when moving points to hurt adversary
    # hyperplane is enable.

    _, defenderTotalSubscriptionNumber = countSubscribersOfHyperplane(defenderHyperplane,
                                                                                 finalMovedPointList,
                                                                         ci= ci)
    _, adversaryTotalSubscriptionNumber = countSubscribersOfHyperplane(adversaryHyperplane,
                                                                               finalMovedPointList, ci = ci)

    if finalMovedPointList == inputPointList or finalMovedPointList == oringinalPointList:
        return False, [], defenderTotalSubscriptionNumber

    if defenderTotalSubscriptionNumber >= adversaryTotalSubscriptionNumber and defenderTotalSubscriptionNumber > 0:
        return True, finalMovedPointList, defenderTotalSubscriptionNumber
    elif defenderTotalSubscriptionNumber == 0:
        raise Exception("The defender total subscription number equals to 0. Bug!")
    else:
        return False, [], defenderTotalSubscriptionNumber


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

def countSubscribersOfHyperplane(inputHyperplane:Hyperplane, inputPointList, ci):  #Attension, when we don't need ci,
    # set ci to be 0.
    pointSubscribedList = []
    totalSubscribeNumber = 0

    for inputPoint in inputPointList:
        pointSubscribed = singlePointSubscribeOfHyperplane(inputHyperplane=inputHyperplane, inputPoint=inputPoint,
                                                           ci = ci)
        if pointSubscribed == 1:
            totalSubscribeNumber += 1
        pointSubscribedList.append(pointSubscribed)
    return pointSubscribedList, totalSubscribeNumber

def singlePointSubscribeOfHyperplane(inputHyperplane:Hyperplane, inputPoint, ci):
    n = []
    for j in range(len(inputPoint)):
        n.append(inputHyperplane.hyperPlaneEquation[j] * inputPoint[j])
    n.append(inputHyperplane.hyperPlaneEquation[-1])
    n = sum(n)
    if n >= ci:
        return 1
    else:
        return 0

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
    getOriginalHyperplaneListWithUtilities(hyperPlaneList, pointList, unbiasedPlane)
    print(hyperPlaneList[1].maximumPointNumber)

# testGetHyperplaneEquation()
# testGetHyperplaneListWithUtilities()