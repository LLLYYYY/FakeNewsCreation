from Multi_Dimension import *
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import sys
import os
import timeit

def mainAlgorithm(outputDirectory, pointDimension = 2, numOfPoint = 150, smallestNormThreshold = 0.1) -> (bool, int):
    """Parameter input: Output parameter. Return run time."""

    functionStartTime = timeit.default_timer()
    outputDirectory = os.path.join(outputDirectory, str(pointDimension)+"D"+str(numOfPoint)+"P")
    if not os.path.isdir(outputDirectory):
        os.mkdir(outputDirectory)


    pointList = []
    storyPointList = []
    storyVectorNumber = 50
    hyperplaneList = []
    smallestL2Norm = 100
    smallestL2NormList = []
    adversaryMaximumPointList = []
    iter = 0
    numOfIteration = []

    for i in range(numOfPoint):
        pointList.append(np.random.ranf(pointDimension).tolist())

    for i in range(storyVectorNumber):
        n = np.random.ranf(pointDimension).tolist()
        storyPointList.append(n)

    while smallestL2Norm > smallestNormThreshold:
        print("Running dimension "+ str(pointDimension)+ " with point number: "+ str(numOfPoint))
        meanStoryPoint = getMeanStoryPoint(storyPointList)
        unbiasedStoryVector = getHyperplaneEquation([meanStoryPoint, [-0.0001]*len(meanStoryPoint)])
        print("The Unbiased story vector is " + str(unbiasedStoryVector.hyperPlaneEquation))

        if (len(smallestL2NormList) > 51) and (abs(smallestL2NormList[-1] - smallestL2NormList[-50]) < 0.001 or \
                smallestL2NormList[-1] - smallestL2NormList[-50] >= 0):  #
            # Prevent
            # Deadloop.
            print("Fail to go further.")
            return False, 0


        iterRange = [i for i in range(numOfPoint)]
        allComb = combinations(iterRange, pointDimension)
        for comb in allComb:
            pointListForHyperplane = []
            for i in comb:
                pointListForHyperplane.append(pointList[i])
            hyperplaneList.append(getHyperplaneEquation(pointListForHyperplane))

        print("Finished getting hyperplane list. The size of the list is " + str(len(hyperplaneList)) + ".")

        getHyperplaneListWithUtilities(hyperplaneList, pointList, unbiasedStoryVector.hyperPlaneEquation)

        print("Finished Getting Lines with Utilities")
        hyperplaneList.sort(key=lambda pair: pair.l2Norm)
        print("Finished Sorting Lines.")

        #Find the best strategy for adversary.
        adversaryHyperplane = HyperPlane([],[])
        for hyperplan in hyperplaneList:
            if hyperplan.maximumPointNumber > adversaryHyperplane.maximumPointNumber:
                adversaryHyperplane = hyperplan

        print("Finished finding the best strategy for adversary")

        # Print the original graph.
        if pointDimension == 2:
            fig = plt.figure()
            plt.scatter(*zip(*pointList))
            defenderPlotLineX, defenderPlotLineY = zip(*hyperplaneList[0].pointList)
            adversaryPlotLineX, adversaryPlotLineY = zip(*adversaryHyperplane.pointList)

            plt.plot(defenderPlotLineX, defenderPlotLineY)
            plt.plot(adversaryPlotLineX, adversaryPlotLineY)

            plt.savefig(os.path.join(outputDirectory, "figure1.png"))
            plt.close(fig)

        # Now iterate the hyperplane list and try to move points.
        for i in range(len(hyperplaneList)):
            if hyperplaneList[i] == adversaryHyperplane:
                print("The defender hyperplane and the adversary hyperplane matched.")
                break

            isSucceed, movedPointList, defenderMaximumPoint, adversaryMaximumPoint = movePoints(hyperplaneList[i],
                                                                                                     adversaryHyperplane,

                                                                                     pointList)

            # if i == len(hyperplaneList) - 2: # For testing and visualization purpose.
            #     print("Debug ploting mode.")
            #     temPointList = movedPointList
            #     if pointDimension == 2:
            #         fig = plt.subplot(2, 2, 3)
            #         plt.scatter(*zip(*temPointList))
            #         defenderPlotLineX, defenderPlotLineY = zip(*hyperplaneList[i].pointList)
            #         adversaryPlotLineX, adversaryPlotLineY = zip(*adversaryHyperplane.pointList)
            #         # fig.set_xlim(left=-1, right=2)
            #         # fig.set_ylim(bottom=-1, top=2)
            #         plt.plot(defenderPlotLineX, defenderPlotLineY)
            #         plt.plot(adversaryPlotLineX, adversaryPlotLineY)
            #     break

            if isSucceed == False:
                continue
            else:
                print("Found defender hyperplane " + str(i) + " that can do better than adversary hyperplane. \n" +
                      "The Defender maximum point count is " + str(defenderMaximumPoint) + "\n" +
                      "The Adversary maximum point count is " + str(adversaryMaximumPoint) + ".")

                # # For Debug purpose.
                # print(hyperplaneList[0].l2Norm,  hyperplaneList[1].l2Norm, hyperplaneList[2].l2Norm)
                # print(hyperplaneList[i].l2Norm)
                # print(hyperplaneList[-1].l2Norm)

                if pointDimension == 2:
                    fig = plt.figure()
                    plt.scatter(*zip(*pointList))
                    defenderPlotLineX, defenderPlotLineY = zip(*hyperplaneList[i].pointList)
                    adversaryPlotLineX, adversaryPlotLineY = zip(*adversaryHyperplane.pointList)
                    # fig.set_xlim(left=-1, right=2)
                    # fig.set_ylim(bottom=-1, top=2)
                    plt.plot(defenderPlotLineX, defenderPlotLineY)
                    plt.plot(adversaryPlotLineX, adversaryPlotLineY)
                    plt.savefig(os.path.join(outputDirectory, "figure2.png"))
                    plt.close(fig)


                pointList = movedPointList

                if pointDimension == 2:
                    fig = plt.figure()
                    plt.scatter(*zip(*pointList))
                    defenderPlotLineX, defenderPlotLineY = zip(*hyperplaneList[i].pointList)
                    adversaryPlotLineX, adversaryPlotLineY = zip(*adversaryHyperplane.pointList)
                    # fig.set_xlim(left=-1, right=2)
                    # fig.set_ylim(bottom=-1, top=2)
                    plt.plot(defenderPlotLineX, defenderPlotLineY)
                    plt.plot(adversaryPlotLineX, adversaryPlotLineY)
                    plt.savefig(os.path.join(outputDirectory, "figure3.png"))
                    plt.close(fig)
                break



        plt.show()
        print("Finished Printing Charts.")

        smallestL2Norm = adversaryHyperplane.l2Norm

        print("Current smallestL2Norm is " + str(smallestL2Norm) + ".\n\n\n")

        iter += 1
        numOfIteration.append(iter)
        smallestL2NormList.append(smallestL2Norm)
        adversaryMaximumPointList.append(adversaryMaximumPoint)

    functionEndTime = timeit.default_timer()

    fig = plt.figure()
    plt.plot(numOfIteration , smallestL2NormList)
    plt.savefig(os.path.join(outputDirectory, "Iter_VS_Def.png"))
    plt.close(fig)

    fig = plt.figure()
    plt.plot(numOfIteration, adversaryMaximumPointList)
    plt.savefig(os.path.join(outputDirectory, "Iter_VS_Adv.png"))
    plt.close(fig)

    return True, (functionEndTime - functionStartTime)

# Run

dimensionList = [2,5,10]
pointNumList = [15, 50, 100, 150, 300, 500, 700, 900, 1000]
dimensionRunTimeList = []
pointNumRunTimeList = []

outputDirectory = sys.argv[1]
if not os.path.isdir(outputDirectory):
    raise Exception("Output Directory not accessible.")

# for dimemsion in dimensionList:
#     isSucceed = False
#     runtimeList = []
#     while not isSucceed:
#         isSucceed, runtime = mainAlgorithm(outputDirectory= outputDirectory, pointDimension=dimemsion, numOfPoint=
#     150)
#         if isSucceed:
#             runtimeList.append(runtime)
#     dimensionRunTimeList.append(sum(runtimeList)/len(runtimeList))

for pointNum in pointNumList:
    isSucceed = False
    runtimeList = []
    while not isSucceed or len(runtimeList) <= 10:
        isSucceed, runtime = mainAlgorithm(outputDirectory=outputDirectory, pointDimension=2, numOfPoint=pointNum)
        if isSucceed:
            runtimeList.append(runtime)
    pointNumRunTimeList.append(sum(runtimeList)/len(runtimeList))

# fig = plt.figure()
# plt.plot( dimensionIter , dimensionRunTimeList)
# plt.savefig(os.path.join(outputDirectory, "Dimension_VS_Runtime.png"))
# plt.close(fig)

fig = plt.figure()
plt.plot( pointNumList , pointNumRunTimeList)
plt.savefig(os.path.join(outputDirectory, "PointNum_VS_Runtime.png"))
plt.close(fig)