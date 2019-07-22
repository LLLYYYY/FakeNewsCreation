import math

def getLineEquation(pointA, pointB):
    if pointA == pointB:
        raise ValueError("Two points are the same")
    A = pointB[1] - pointA[1]
    B = pointA[0] - pointB[0]
    C = pointB[0]*pointA[1] - pointA[0] * pointB[1]
    if B < 0: # B has to be larger than 0
        A = -A
        B = -B
        C = -C
    outputLine = [[A,B,C],[pointA,pointB]]
    return outputLine

def getMeanLine(inputStoryVectorList):
    """Input story vector list, return unbiased mean line."""
    if not inputStoryVectorList:
        raise ValueError("The inputPointList is empty. Please check the input point list.")

    meanLine = []
    for i in range(len(inputStoryVectorList[0])):
        n = 0
        for line in inputStoryVectorList:
            n += line[i]
        n /= len(inputStoryVectorList[0])
        meanLine.append(n)

    # meanLine.append(0) # This is the constant value.
    return meanLine

def getOrthogonalUnitVector(inputLine):
    """Input single line. Not a line list. Return Orthogonal Unit Vector."""
    if inputLine[0][1] == 0:
        return [1,0]

    k = -inputLine[0][0] / inputLine[0][1]
    if k == 0:
        return [0,1]
    else:
        k = - 1 / k
        mag = math.sqrt(1 ** 2 + k ** 2)
        mag *= 5 # Decrease moving distance.
        if k/mag > 0:
            return [1/mag, k/mag]
        else:
            return [-1/mag, -k/mag]

def getLineListWithUtilities(inputLineList, inputPointList, unbiasedLine):

    """Return line list with utilities. The format of line list is :
        [[[line],[pointA, pointB]],[point number in the side with more points, upperPointNumber, lowerPointNumber,
        onLinePointNumber],
        L2Norm]
        Also return the closest line to the unbiased line.
    """
    lineListWithUtilities = []
    smallestNorm = 0
    smallestNormLine = []
    for i in range(len(inputLineList)):
        upperPointNumber = 0
        lowerPointNumber = 0
        onLinePointNumber = 0
        for j in range(len(inputPointList)):
            n = inputLineList[i][0][0] * inputPointList[j][0] + inputLineList[i][0][1] * inputPointList[j][1] + \
                inputLineList[i][0][2]
            if n > 0:
                upperPointNumber += 1
            elif n < 0:
                lowerPointNumber += 1
            else:
                onLinePointNumber += 1

        if upperPointNumber > lowerPointNumber:
            countedPointNumber = upperPointNumber + onLinePointNumber
        else:   # include upper == lower
            countedPointNumber = lowerPointNumber + onLinePointNumber

        # L2 Norm:
        norm = 0
        for k in range(len(inputLineList[i][0])):
            norm += (inputLineList[i][0][k] - unbiasedLine[k]) ** 2
        norm = math.sqrt(norm)

        lineWithUtilities = [inputLineList[i],[countedPointNumber, upperPointNumber, lowerPointNumber,
                                               onLinePointNumber], norm]

        lineListWithUtilities.append(lineWithUtilities)

        if norm < smallestNorm:
            smallestNorm = norm
            smallestNormLine = lineWithUtilities


    return lineListWithUtilities, smallestNormLine

def movePoints(inputLineWithUtilities, inputPointList):
    """Return moved points list."""
    movedPointsList = []
    # print(inputLineWithUtilities[1])
    if inputLineWithUtilities[1][0] == inputLineWithUtilities[1][1] + inputLineWithUtilities[1][3]: # Upper has more
        for point in inputPointList:
            if point[0]*inputLineWithUtilities[0][0][0] + point[1]*inputLineWithUtilities[0][0][1] + \
                    inputLineWithUtilities[0][0][2] < 0  and  (abs(point[0]*inputLineWithUtilities[0][0][0] + point[1]*inputLineWithUtilities[0][0][1] + \
                    inputLineWithUtilities[0][0][2])) / (math.sqrt(inputLineWithUtilities[0][0][0]**2 +
                                                                       inputLineWithUtilities[0][0][1] ** 2)) <= 0.2:
                #Upper has more. Move lower
                movedPoint = [x + y for x, y in zip(point, getOrthogonalUnitVector(inputLineWithUtilities[0]))]
                # print(movedPoint)
                movedPointsList.append(movedPoint)
            else:
                movedPointsList.append(point)
    elif inputLineWithUtilities[1][0] == inputLineWithUtilities[1][2] + inputLineWithUtilities[1][3]: # Lower has more
    # else:
        for point in inputPointList:
            if point[0] * inputLineWithUtilities[0][0][0] + point[1] * inputLineWithUtilities[0][0][1] + \
                    inputLineWithUtilities[0][0][2] > 0 \
                and (abs(point[0] * inputLineWithUtilities[0][0][0] + point[1] * inputLineWithUtilities[0][0][1] + \
                         inputLineWithUtilities[0][0][2])) / (math.sqrt(inputLineWithUtilities[0][0][0] ** 2 + \
                                                                            inputLineWithUtilities[0][0][1] ** 2)) <=\
                    0.2: #lower has more. Move upper
                print(getOrthogonalUnitVector(getOrthogonalUnitVector(inputLineWithUtilities[0])))
                movedPoint = [x - y for x,y in zip(point, getOrthogonalUnitVector(inputLineWithUtilities[0]))]
                movedPointsList.append(movedPoint)
            else:
                movedPointsList.append(point)
    else:
        raise ValueError("Crash at movedPointList")
        ##########################Haven't implemented!!!!!!!!!!!!!!!!!!

    # print(movedPointsList)

    return movedPointsList



#### The following code is for testing purpose.
def testing():
    pass
    # pointA = [3,2]
    # pointB = [3,3]
    # lineEquation = getLineEquation(pointA,pointB)
    # orthogonalUnitVector = getOrthogonalUnitVector(lineEquation)
    # print(lineEquation)
    # print(orthogonalUnitVector)
    #
    # pointA = [2,3]
    # pointB = [3,3]
    # lineEquation = getLineEquation(pointA,pointB)
    # orthogonalUnitVector = getOrthogonalUnitVector(lineEquation)
    # print(lineEquation)
    # pointA = [3,2]
    # print(orthogonalUnitVector)
    #
    # pointA = [2,3]
    # pointB = [3,2]
    # lineEquation = getLineEquation(pointA,pointB)
    # orthogonalUnitVector = getOrthogonalUnitVector(lineEquation)
    # print(lineEquation)
    # print(orthogonalUnitVector)
    #
    # pointA = [0,0]
    # pointB = [3,2]
    # lineEquation = getLineEquation(pointA,pointB)
    # orthogonalUnitVector = getOrthogonalUnitVector(lineEquation)
    # print(lineEquation)
    # print(orthogonalUnitVector)
    #
    # pointA = [2,0]
    # pointB = [3,2]
    # lineEquation = getLineEquation(pointA,pointB)
    # orthogonalUnitVector = getOrthogonalUnitVector(lineEquation)
    # print(lineEquation)
    # print(orthogonalUnitVector)

