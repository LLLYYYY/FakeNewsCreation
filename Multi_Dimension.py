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


    if hyperplaneEauation[1] < 0:
        hyperplaneEauation = [-x for x in hyperplaneEauation]

    if hyperplaneEauation[1] == 0:
        raise ValueError("Hyperplane parallel to the y axis. Error!")
    else:
        devider = hyperplaneEauation[1]
        hyperplaneEauation = [x/devider for x in hyperplaneEauation]

    outputHyperplaneEquation = Hyperplane(hyperPlaneEquation = hyperplaneEauation)
    return outputHyperplaneEquation

def getOrthogonalUnitVector(inputHyperplane:Hyperplane):
    orthogonalVector = inputHyperplane.hyperPlaneEquation[:-1]
    meg = math.sqrt(sum([x**2 for x in orthogonalVector]))

    orthogonalUnitVector = [ x/meg for x in orthogonalVector]
    if orthogonalUnitVector[1] < 0:  #Just in case. Not gonna happen.
        orthogonalUnitVector = [-x for x in orthogonalUnitVector]

    return orthogonalUnitVector

def getOriginalHyperplaneListWithUtilities2(inputHyperPlaneList: [Hyperplane], consumerPointList, unbiasedVector):

    """Return hyperPlane list with utilities.
        Dimension Free.
        InputHyperPlaneList is a Hyperplane instance. But UnbiasedVector is just a vector list.
    """

    for i in range(len(inputHyperPlaneList)):

        inputHyperPlaneList[i].pointSubscription, inputHyperPlaneList[i].adversaryUtility = \
            countSubscribersOfHyperplane2(
            inputHyperPlaneList[i], consumerPointList, ci)

        # L2 Norm:
        norm = 0

        #get unit vector for unbiased vector and hyperplaneEquation
        # Change the normal vector to unit vector.
        unbiasedVector2 = unbiasedVector
        unbiasedVecMagnitude = (sum([x ** 2 for x in unbiasedVector[:-1]])) ** 0.5
        if unbiasedVecMagnitude != 0:
             unbiasedVector2 = [x/unbiasedVecMagnitude for x in unbiasedVector]
        else:
             raise ValueError("Getting a all zeros hyperplane.")
        # Change the hyperplane vector to unit vector.
        currHyperplane = inputHyperPlaneList[i].hyperPlaneEquation
        hyperplaneMagnitude = (sum([x ** 2 for x in inputHyperPlaneList[i].hyperPlaneEquation[:-1]])) ** 0.5
        if hyperplaneMagnitude != 0:
            currHyperplane = [x / hyperplaneMagnitude for x in inputHyperPlaneList[i].hyperPlaneEquation]
        else:
            raise ValueError("Getting a all zeros hyperplane.")

        #for k in range(len(inputHyperPlaneList[i].hyperPlaneEquation)-1): # Don't count the constant variable???  Not
            # counting now.
        for k in range(len(currHyperplane)-1):
            #TODO: It is possible that hyperplaneequation[1] == 0. It will crush.
            norm += (currHyperplane[k] - unbiasedVector2[k]) ** 2
            #norm += (inputHyperPlaneList[i].hyperPlaneEquation[k]/inputHyperPlaneList[i].hyperPlaneEquation[1] -
            #unbiasedVector[k]/unbiasedVector[1]) ** 2  # When calculating the norm, I keep the y parameter to be 1.
        norm = math.sqrt(norm)

        inputHyperPlaneList[i].defenderUtility = norm
    return inputHyperPlaneList


def getOriginalHyperplaneListWithUtilities(inputHyperPlaneList: [Hyperplane], consumerPointList, unbiasedVector):

    """Return hyperPlane list with utilities.
        Dimension Free.
        InputHyperPlaneList is a Hyperplane instance. But UnbiasedVector is just a vector list.
    """

    for i in range(len(inputHyperPlaneList)):

        inputHyperPlaneList[i].pointSubscription, inputHyperPlaneList[i].adversaryUtility = \
            countSubscribersOfHyperplane(
            inputHyperPlaneList[i], consumerPointList, ci)

        # L2 Norm:
        norm = 0
        # get unit vector for unbiased vector and hyperplaneEquation
        # Change the normal vector to unit vector.
        unbiasedVector2 = unbiasedVector
        unbiasedVecMagnitude = (sum([x ** 2 for x in unbiasedVector[:-1]])) ** 0.5
        if unbiasedVecMagnitude != 0:
            unbiasedVector2 = [x / unbiasedVecMagnitude for x in unbiasedVector]
        else:
            raise ValueError("Getting a all zeros hyperplane.")
        # Change the hyperplane vector to unit vector.
        currHyperplane = inputHyperPlaneList[i].hyperPlaneEquation
        hyperplaneMagnitude = (sum([x ** 2 for x in inputHyperPlaneList[i].hyperPlaneEquation[:-1]])) ** 0.5
        if hyperplaneMagnitude != 0:
            currHyperplane = [x / hyperplaneMagnitude for x in inputHyperPlaneList[i].hyperPlaneEquation]
        else:
            raise ValueError("Getting a all zeros hyperplane.")


        for k in range(len(currHyperplane)-1): # Don't count the constant variable???  Not
            # counting now.
            #TODO: It is possible that hyperplaneequation[1] == 0. It will crush.
            norm += (currHyperplane[k] - unbiasedVector2[k]) ** 2
            #norm += (inputHyperPlaneList[i].hyperPlaneEquation[k]/inputHyperPlaneList[i].hyperPlaneEquation[1] -
            #unbiasedVector[k]/unbiasedVector[1]) ** 2  # When calculating the norm, I keep the y parameter to be 1.
        norm = math.sqrt(norm)

        inputHyperPlaneList[i].defenderUtility = norm
    return inputHyperPlaneList

def getConvertedHyperplaneListWithUtilities(originalConvertedHyperplaneMatchList: [[Hyperplane, Hyperplane]],
                                            consumerPointList, unbiasedVector, ci):
    """Dimension Free."""
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
        # get unit vector for unbiased vector and hyperplaneEquation
        # Change the normal vector to unit vector.
        unbiasedVector2 = unbiasedVector
        unbiasedVecMagnitude = (sum([x ** 2 for x in unbiasedVector[:-1]])) ** 0.5
        if unbiasedVecMagnitude != 0:
            unbiasedVector2 = [x / unbiasedVecMagnitude for x in unbiasedVector]
        else:
            raise ValueError("Getting a all zeros hyperplane.")
        # Change the hyperplane vector to unit vector.
        currHyperplane = convertedHyperplaneList[i].hyperPlaneEquation
        hyperplaneMagnitude = (sum([x ** 2 for x in convertedHyperplaneList[i].hyperPlaneEquation[:-1]])) ** 0.5
        if hyperplaneMagnitude != 0:
            currHyperplane = [x / hyperplaneMagnitude for x in convertedHyperplaneList[i].hyperPlaneEquation]
        else:
            raise ValueError("Getting a all zeros hyperplane.")

        for k in range(len(currHyperplane) - 1):  # Don't count the constant variable???  Not
            # counting now.
            # TODO: It is possible that hyperplaneequation[1] == 0. It will crush.
            norm += (currHyperplane[k] - unbiasedVector2[k]) ** 2
            #norm += (convertedHyperplaneList[i].hyperPlaneEquation[k] / convertedHyperplaneList[i].hyperPlaneEquation[1] -
            #         unbiasedVector[k] / unbiasedVector[1]) ** 2  # When calculating the norm, I keep the y parameter to be 1.
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

            if distanceToOriginalPoints <= longestMovingDistance and singlePointSubscribeOfHyperplane(
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

    _, defenderTotalSubscriptionNumber = countSubscribersOfHyperplane(defenderHyperplane,
                                                                                 finalMovedPointList,
                                                                         ci= ci)
    _, adversaryTotalSubscriptionNumber = countSubscribersOfHyperplane(adversaryHyperplane,
                                                                               finalMovedPointList, ci = ci)

    # if finalMovedPointList == inputPointList or finalMovedPointList == oringinalPointList:
    #     return False, [], defenderTotalSubscriptionNumber

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

def countSubscribersOfHyperplane2(inputHyperplane:Hyperplane, inputPointList, ci):  #Attension, when we don't need ci,
    # set ci to be 0.
    pointSubscribedList = []
    totalSubscribeNumber = 0

    for inputPoint in inputPointList:
        pointSubscribed = singlePointSubscribeOfHyperplane2(inputHyperplane=inputHyperplane, inputPoint=inputPoint,
                                                           ci = ci)
        if pointSubscribed == 1:
            totalSubscribeNumber += 1
        pointSubscribedList.append(pointSubscribed)
    return pointSubscribedList, totalSubscribeNumber

#to be used by original generated hyperplanes, which have a constant term and do not need ci
def singlePointSubscribeOfHyperplane2(inputHyperplane:Hyperplane, inputPoint, ci):
    n = []
    for j in range(len(inputPoint)):
        n.append(inputHyperplane.hyperPlaneEquation[j] * inputPoint[j])
    n.append(inputHyperplane.hyperPlaneEquation[-1])  # Re-enable the constant variable.
    n = sum(n)
    if n>=0:
        return 1
    else:
        return 0


def debugsinglePointSubscribeOfHyperplane2(inputHyperplane:Hyperplane, inputPoint, ci):
    n = []
    for j in range(len(inputPoint)):
        n.append(inputHyperplane.hyperPlaneEquation[j] * inputPoint[j])
    n.append(inputHyperplane.hyperPlaneEquation[-1])  # Re-enable the constant variable.
    n = sum(n)
    print(n)
    #if n > 0 - precisionError:
    if n>=0:
        return 1
    else:
        return 0

#to be used by converted hyperplane directions, which have no constant term other than ci
def singlePointSubscribeOfHyperplane(inputHyperplane:Hyperplane, inputPoint, ci):
    n = []
    for j in range(len(inputPoint)):
        n.append(inputHyperplane.hyperPlaneEquation[j] * inputPoint[j])
    #n.append(inputHyperplane.hyperPlaneEquation[-1])  # Re-enable the constant variable.
    n = sum(n)
    n=n-ci
    if n >=-1*precisionError and n<=0:
        n=0
    if n>=0:
        return 1
    else:
        return 0

def debugsinglePointSubscribeOfHyperplane(inputHyperplane:Hyperplane, inputPoint, ci):
    n = []
    for j in range(len(inputPoint)):
        n.append(inputHyperplane.hyperPlaneEquation[j] * inputPoint[j])
    #n.append(inputHyperplane.hyperPlaneEquation[-1])  # Re-enable the constant variable.
    n = sum(n)
    n=n-ci
    print(n)
    if n >=-1*precisionError and n<=0:
        n=0
    #if n > 0 - precisionError:
    if n>=0:
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