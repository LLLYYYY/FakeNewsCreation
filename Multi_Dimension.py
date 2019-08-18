import math
import numpy as np
from DataStructure import *
from config import *

def getMeanHyperplane(inputStoryVectorList):
    """Input story vector list, return unbiased mean line.
        This function is dimension free.
    """
    if inputStoryVectorList.size == 0:
        raise ValueError("The consumerPointList is empty. Please check the input point list.")

    meanPoint = inputStoryVectorList.sum(axis=0) / len(inputStoryVectorList)

    if np.count_nonzero(meanPoint) == 0:
        raise ValueError("The unbiased vector contains all zeros parameters.")

    meanHyperplane = Hyperplane(np.append(meanPoint,[0]))
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
    hyperplaneMatrix = np.linalg.solve(pointMatrix, b)
    hyperplaneEauation = hyperplaneMatrix
    hyperplaneEauation = np.append(hyperplaneEauation, -1)

    outputHyperplaneEquation = Hyperplane(hyperPlaneEquation = hyperplaneEauation)
    return outputHyperplaneEquation

def getOrthogonalUnitVector(inputHyperplane):
    """The return vector is a unit vector."""
    orthogonalVector = inputHyperplane.hyperPlaneEquation[:-1]
    meg = math.sqrt(np.sum(orthogonalVector ** 2))

    orthogonalUnitVector = orthogonalVector / meg
    if orthogonalUnitVector[1] < 0:
        orthogonalUnitVector = -orthogonalVector

    return orthogonalUnitVector

def getOriginalHyperplaneListWithUtilities(inputHyperPlaneList, consumerPointList, unbiasedVector):

    """Return hyperPlane list with utilities.
        Dimension Free.
        InputHyperPlaneList is a Hyperplane instance. But UnbiasedVector is just a vector list.
    """

    for i in range(len(inputHyperPlaneList)):

        inputHyperPlaneList[i].pointSubscription, inputHyperPlaneList[i].adversaryUtility = \
            countSubscribersOfOriginalHyperplane(
            inputHyperPlaneList[i], consumerPointList)

        # L2 Norm:
        currHyperplaneEquationWithoutC = inputHyperPlaneList[i].hyperPlaneEquation[:-1]
        currUnbiasedVectorWithoutC = unbiasedVector[:-1]
        norm = math.sqrt(np.sum((currHyperplaneEquationWithoutC - currUnbiasedVectorWithoutC) ** 2))

        inputHyperPlaneList[i].defenderUtility = norm
    return inputHyperPlaneList

def getConvertedHyperplaneListWithUtilities(originalConvertedHyperplaneMatchList,
                                            consumerPointList, unbiasedVector, ci):
    """Dimension Free."""
    originalHyperplaneList = [originalConvertedHyperplaneMatchList[i][0] for i in range(len(originalConvertedHyperplaneMatchList))]
    convertedHyperplaneList = [originalConvertedHyperplaneMatchList[i][1] for i in range(len(
        originalConvertedHyperplaneMatchList))]

    for i in range(len(convertedHyperplaneList)):
        convertedHyperplaneList[i].pointSubscription, convertedHyperplaneList[i].adversaryUtility = \
            countSubscribersOfConvertedHyperplane(
            convertedHyperplaneList[i], consumerPointList,  ci)

        # if convertedHyperplaneList[i].pointSubscription != originalHyperplaneList[i].pointSubscription:
        if not np.array_equal(convertedHyperplaneList[i].pointSubscription, originalHyperplaneList[
            i].pointSubscription):
            raise ValueError("The converted hyperplane has different point subscription compare to the original.")

        # L2 Norm:
        norm = 0
        currHyperplaneEquationWithoutC = convertedHyperplaneList[i].hyperPlaneEquation[:-1]
        currUnbiasedVectorWithoutC = unbiasedVector[:-1]
        norm = math.sqrt(np.sum((currHyperplaneEquationWithoutC - currUnbiasedVectorWithoutC) ** 2))
        convertedHyperplaneList[i].defenderUtility = norm
    return convertedHyperplaneList



def twoPointsDistance (pointA, pointB):
    dimension = len(pointA)
    distance = 0
    for i in range(dimension):
        distance += ( pointB[i] - pointA[i]) * ( pointB[i] - pointA[i])
    distance = math.sqrt(distance)
    return distance



def movePoints(defenderHyperplane, adversaryHyperplane, inputPointList, oringinalPointList, ci):
    """Try to move points so that the defender hyperplane can has more point counts than adversary hyperplane.
        If succeed, return True, finalMovedPointList, defenderMaximumPointNumber, adveraryMaximumPointNumber
        If failed, return False, [empty list], defenderMaximumPointNumber, adveraryMaximumPointNumber
    """
    movedDefenderPointsList = []
    finalMovedPointList = []

    # Move points to benefits defender.
    for i in range(len(inputPointList)):
        if defenderHyperplane.pointSubscription[i] == 0:
            beta = []
            gamma = []
            normalUnitVector = getOrthogonalUnitVector(defenderHyperplane)
            for j in range(len(inputPointList[i])):
                beta.append(inputPointList[i][j] * defenderHyperplane.hyperPlaneEquation[j])
                gamma.append(normalUnitVector[j] * defenderHyperplane.hyperPlaneEquation[j])

            beta = sum(beta)
            gamma = sum(gamma)

            lowerBoundonDistance = (ci - beta)/ gamma

            movedPoint = [x + y for x, y in
                          zip(inputPointList[i], [lowerBoundonDistance * z for z in getOrthogonalUnitVector(
                              defenderHyperplane)])]

            distanceToOriginalPoints = twoPointsDistance(oringinalPointList[i], movedPoint)

            if distanceToOriginalPoints <= longestMovingDistance and singlePointSubscribeOfConvertedHyperplane(
                    defenderHyperplane, movedPoint, ci) == 1:
                movedDefenderPointsList.append(movedPoint)
            else:
                movedDefenderPointsList.append(inputPointList[i]) # Not moving this point because the total moving
                # distance is too large or cannot change the subscription status.
        else:
            movedDefenderPointsList.append(inputPointList[i]) # This point is already subscribed.



    # #     ##########################Haven't implemented!!!!!!!!!!!!!!!!!!

    finalMovedPointList = movedDefenderPointsList # TODO: Delete this line when moving points to hurt adversary
    # hyperplane is enable.

    _, defenderTotalSubscriptionNumber = countSubscribersOfConvertedHyperplane(defenderHyperplane,
                                                                                 finalMovedPointList,
                                                                         ci= ci)
    _, adversaryTotalSubscriptionNumber = countSubscribersOfConvertedHyperplane(adversaryHyperplane,
                                                                               finalMovedPointList, ci = ci)

    if np.array_equal(finalMovedPointList, inputPointList) or np.array_equal(finalMovedPointList, oringinalPointList):
        return False, [], defenderTotalSubscriptionNumber

    if defenderTotalSubscriptionNumber >= adversaryTotalSubscriptionNumber and defenderTotalSubscriptionNumber > 0:
        return True, finalMovedPointList, defenderTotalSubscriptionNumber
    elif defenderTotalSubscriptionNumber == 0:
        raise Exception("The defender total subscription number equals to 0. Bug!")
    else:
        return False, [], defenderTotalSubscriptionNumber


def isTwoPointsOnTheSameSideOfHyperplane(pointA, pointB, hyperplane):

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

def countSubscribersOfConvertedHyperplane(inputHyperplane, inputPointList, ci):
    pointSubscribedList = np.empty(len(inputPointList))
    totalSubscribeNumber = 0

    for i in range(len(inputPointList)):
        pointSubscribed = singlePointSubscribeOfConvertedHyperplane(inputHyperplane=inputHyperplane,
                                                                    inputPoint=inputPointList[i],
                                                           ci = ci)
        if pointSubscribed == 1:
            totalSubscribeNumber += 1
        pointSubscribedList[i] = pointSubscribed
    return pointSubscribedList, totalSubscribeNumber

def countSubscribersOfOriginalHyperplane(inputHyperplane, inputPointList):
    pointSubscribedList = np.empty(len(inputPointList))
    totalSubscribeNumber = 0

    for i in range(len(inputPointList)):
        pointSubscribed = singlePointSubscribeOfOriginalHyperplane(inputHyperplane=inputHyperplane,
                                                                   inputPoint=inputPointList[i])
        if pointSubscribed == 1:
            totalSubscribeNumber += 1
        pointSubscribedList[i] = pointSubscribed
    return pointSubscribedList, totalSubscribeNumber

#to be used by original generated hyperplanes, which have a constant term and do not need ci
def singlePointSubscribeOfOriginalHyperplane(inputHyperplane, inputPoint):
    n = np.dot(inputHyperplane.hyperPlaneEquation[:-1], inputPoint)
    n += inputHyperplane.hyperPlaneEquation[-1]
    if n>=0:
        return 1
    else:
        return 0

def singlePointSubscribeOfConvertedHyperplane(inputHyperplane, inputPoint, ci):
    n = np.dot(inputHyperplane.hyperPlaneEquation[:-1], inputPoint)
    n += inputHyperplane.hyperPlaneEquation[-1]
    n=n-ci
    if n >=-1*precisionError and n<=0:
        n=0
    if n>=0:
        return 1
    else:
        return 0


# def debugsinglePointSubscribeOfHyperplane2(inputHyperplane:Hyperplane, inputPoint, ci):
#     n = []
#     for j in range(len(inputPoint)):
#         n.append(inputHyperplane.hyperPlaneEquation[j] * inputPoint[j])
#     n.append(inputHyperplane.hyperPlaneEquation[-1])  # Re-enable the constant variable.
#     n = sum(n)
#     # print(n)
#     #if n > 0 - precisionError:
#     if n>=0:
#         return 1
#     else:
#         return 0

# def debugsinglePointSubscribeOfHyperplane(inputHyperplane:Hyperplane, inputPoint, ci):
#     n = []
#     for j in range(len(inputPoint)):
#         n.append(inputHyperplane.hyperPlaneEquation[j] * inputPoint[j])
#     #n.append(inputHyperplane.hyperPlaneEquation[-1])  # Re-enable the constant variable.
#     n = sum(n)
#     n=n-ci
#     # print(n)
#     if n >=-1*precisionError and n<=0:
#         n=0
#     #if n > 0 - precisionError:
#     if n>=0:
#         return 1
#     else:
#         return 0

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