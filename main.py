from Multi_Dimension import *
from HyperplaneConversion import *
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import sys
import os
import timeit
from cplex.exceptions.errors import *
plt.switch_backend('agg')

def mainAlgorithm(outputDirectory, pointDimension = 2, numOfPoint = 150, smallestNormThreshold = 0.1, runCount = 0) -> (
        bool, int):
    """Parameter input: Output parameter. Return run time."""
    #Already changed to storyVector hyperplane calculation.

    functionStartTime = timeit.default_timer()
    outputDirectory = os.path.join(outputDirectory, str(pointDimension)+"D"+str(numOfPoint)+"P")
    if not os.path.isdir(outputDirectory):
        os.mkdir(outputDirectory)
    outputDirectory = os.path.join(outputDirectory, str(runCount))
    if not os.path.isdir(outputDirectory):
        os.mkdir(outputDirectory)


    pointList = []
    originalPointList = []
    storyPointList = []
    storyVectorNumber = 50
    hyperplaneList = []
    smallestL2NormList = []
    adversaryMaximumPointList = []
    iter = 0
    ci = 1
    numOfIteration = []
    adversaryMaximumPoint = 0
    originalConvertedHyperplaneMatchList = []
    # movedPointList = []

    epsilon = 0.001 # Use for determine the minimum l2norm change.

    for i in range(numOfPoint):
        pointList.append([ 2*x-1 for x in np.random.ranf(pointDimension).tolist()])
    originalPointList = pointList

    for i in range(storyVectorNumber):
        storyPointList.append([ 2*x-1 for x in np.random.ranf(pointDimension).tolist()])
    unbiasedStoryVector = getMeanHyperplane(storyPointList)

    while len(smallestL2NormList) <= 1 or ( len(smallestL2NormList) > 1 and abs(smallestL2NormList[-1] -
                                                                               smallestL2NormList[-2]) > epsilon):
        print("Running dimension " + str(pointDimension)+ " with point number: "+ str(numOfPoint))
        print("The Unbiased story vector is " + str(unbiasedStoryVector.hyperPlaneEquation))

        plotOutputDirectory = os.path.join(outputDirectory, str(iter))
        if not os.path.isdir(plotOutputDirectory):
            os.mkdir(plotOutputDirectory)

        iterRange = [i for i in range(numOfPoint)]
        allComb = combinations(iterRange, pointDimension)
        for comb in allComb:
            pointListForHyperplane = []
            for i in comb:
                pointListForHyperplane.append(pointList[i])
            hyperplaneList.append(getHyperplaneEquation(pointListForHyperplane))
        print("Finished getting hyperplane list. The size of the list is " + str(len(hyperplaneList)) + ".")

        getHyperplaneListWithUtilities(hyperplaneList, pointList, unbiasedStoryVector.hyperPlaneEquation,
                                       inputStoryVector=storyPointList, ci= ci)

        print("Finished Getting Lines with Utilities")

        convertedHyperplaneList = []
        for hyperplane in hyperplaneList:
            try:
                convertedHyperplane = hyperPlaneConversion(hyperplane, pointList, storyPointList)
                convertedHyperplaneList.append(convertedHyperplane)
                originalConvertedHyperplaneMatchList.append([hyperplane, convertedHyperplane])
            except CplexSolverError:
                print("\n\n\n\n\n\n\n\n Failed to generated hyperplane. \n\n\n\n\n\n\n\n\n")
                continue

        print("Finished converting hyperplanes.  The size of the convert hyperplanelist is:" + str(len(
            convertedHyperplaneList)) + ".")

        hyperplaneList = convertedHyperplaneList

        getHyperplaneListWithUtilities(hyperplaneList, pointList, unbiasedStoryVector.hyperPlaneEquation,
                                       inputStoryVector=storyPointList, ci=ci)
        print("Finished Getting Lines with Utilities No2.")


        # Now plot the original and converted hyperplane.
        plotOriginalHyperplaneList = []
        plotConvertedHyperplaneList = []
        if len(originalConvertedHyperplaneMatchList) < 3:
            print("Failed to convert enough hyperplane.")
            break
        for p in range(3):
            matchedHyperplane = originalConvertedHyperplaneMatchList[p]
            plotOriginalHyperplaneList.append(matchedHyperplane[0])
            plotConvertedHyperplaneList.append(matchedHyperplane[1])
        plotHyperplaneList(pointList, plotOriginalHyperplaneList, plotOutputDirectory, "figure1.png")
        plotHyperplaneList(pointList, plotConvertedHyperplaneList, plotOutputDirectory, "figure2.png")

        print("Finished printing the original and converted hyperplane charts.")

        # # After regenerating the hyperplane. Needs to recalculate the L2Norm.
        # getHyperplaneListWithUtilities(hyperplaneList, pointList, unbiasedStoryVector.hyperPlaneEquation,
        #                                inputStoryVector=storyPointList, ci=ci)
        #
        # print("Finished Getting Lines with Utilities No2")

        hyperplaneList.sort(key=lambda pair: pair.l2Norm)
        print("Finished Sorting Lines.")

        #Find the best strategy for adversary.
        adversaryHyperplane = Hyperplane([], [])
        defenderHyperplane = Hyperplane([], [])
        for hyperplane in hyperplaneList:
            if hyperplane.maximumPointNumber > adversaryHyperplane.maximumPointNumber:
                adversaryHyperplane = hyperplane


        print("Finished finding the best strategy for adversary")

        # Print the original graph.
        if pointDimension == 2:
            plotDefAdvHyperplane(pointList, hyperplaneList[0].hyperPlaneEquation,
                                 adversaryHyperplane.hyperPlaneEquation, plotOutputDirectory, "figure3.png")

        # Now iterate the hyperplane list and try to move points.
        for i in range(len(hyperplaneList)):
            if hyperplaneList[i] == adversaryHyperplane:
                print("The defender hyperplane and the adversary hyperplane matched. List number: " + str(i))
                break

            isSucceed, movedPointList, defenderMaximumPoint, adversaryMaximumPoint = movePoints(hyperplaneList[i],
                                                                                                     adversaryHyperplane,

                                                                                     pointList, originalPointList,
                                                                                                ci=ci)

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

                if movedPointList == pointList:
                    print("Points not moving.")
                    continue

                print("Found defender hyperplane " + str(i) + " that can do better than adversary hyperplane. \n" +
                      "The Defender maximum point count is " + str(defenderMaximumPoint) + "\n" +
                      "The Adversary maximum point count is " + str(adversaryMaximumPoint) + ".")

                defenderHyperplane = hyperplaneList[i]

                # # For Debug purpose.
                # print(hyperplaneList[0].l2Norm,  hyperplaneList[1].l2Norm, hyperplaneList[2].l2Norm)
                # print(hyperplaneList[i].l2Norm)
                # print(hyperplaneList[-1].l2Norm)

                if pointDimension == 2:
                    plotDefAdvHyperplane(pointList, defenderHyperplane.hyperPlaneEquation,
                                         adversaryHyperplane.hyperPlaneEquation, plotOutputDirectory, "figure4.png")

                pointList = movedPointList

                if pointDimension == 2:
                    plotDefAdvHyperplane(pointList, defenderHyperplane.hyperPlaneEquation,
                                         adversaryHyperplane.hyperPlaneEquation, plotOutputDirectory, "figure5.png")
                break

        plt.show()
        print("Finished Printing Charts.")

        smallestL2Norm = defenderHyperplane.l2Norm

        print("Current smallestL2Norm is " + str(smallestL2Norm) + ".\n\n\n")

        functionEndTime = timeit.default_timer()

        #TODO: Will cause bugs. NOT sure why.
        # if movedPointList == originalPointList:
        #     return False, (functionEndTime - functionStartTime)

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

def plotDefAdvHyperplane(pointList, defenderHyperplaneEquation, adversaryHyperplaneEquation, plotOutputDirectory, plotFileName):
    """Attension: Only works in two dimension..."""
    if not pointList:
        if len(pointList[0]) != 2:
            return

    fig = plt.figure()
    plt.scatter(*zip(*pointList))
    defenderPlotLineX = [-1, 1]
    adversaryPlotLineX = [-1, 1]

    defenderPlotLineY = [defenderHyperplaneEquation[0] / defenderHyperplaneEquation[1] - defenderHyperplaneEquation[
        2] / defenderHyperplaneEquation[1], -defenderHyperplaneEquation[0] / defenderHyperplaneEquation[1] -
                         defenderHyperplaneEquation[
                             2] / defenderHyperplaneEquation[1]]
    adversaryPlotLineY = [
        adversaryHyperplaneEquation[0] / adversaryHyperplaneEquation[1] - adversaryHyperplaneEquation[
            2] / adversaryHyperplaneEquation[1],
        -adversaryHyperplaneEquation[0] / adversaryHyperplaneEquation[1] - adversaryHyperplaneEquation[
            2] / adversaryHyperplaneEquation[1]]
    plt.plot(defenderPlotLineX, defenderPlotLineY)
    plt.plot(adversaryPlotLineX, adversaryPlotLineY)
    plt.savefig(os.path.join(plotOutputDirectory, plotFileName))
    plt.close(fig)

    return

def plotHyperplaneList(pointList, hyperplaneList, plotOutputDirectory, plotFileName):
    """Attension: Only works in two dimension..."""
    if not pointList:
        if len(pointList[0]) != 2:
            return

    fig = plt.figure()
    plt.scatter(*zip(*pointList))
    plotLineListX = []
    plotLineListY = []
    for hyperplane in hyperplaneList:
        hyperplaneEquation = hyperplane.hyperPlaneEquation
        plotLineListX.append([-1,1])
        plotLineListY.append([hyperplaneEquation[0] / hyperplaneEquation[1] - hyperplaneEquation[
        2] / hyperplaneEquation[1], -hyperplaneEquation[0] / hyperplaneEquation[1] -
                         hyperplaneEquation[
                             2] / hyperplaneEquation[1]])

    for i in range(len(plotLineListX)):
        plt.plot(plotLineListX[i],plotLineListY[i])
    plt.savefig(os.path.join(plotOutputDirectory, plotFileName))
    plt.close(fig)

    return

# Run

dimensionList = [2,3,4]#,3,4,5]
pointNumList = [20,50,80, 100]#, 30, 40, 50, 70, 90]#, 100]# , 120, 150]#, 500, 700, 900, 1000]
dimensionRunTimeList = []
pointNumRunTimeList = []

outputDirectory = sys.argv[1]
if not os.path.isdir(outputDirectory):
    raise Exception("Output Directory not accessible.")

# for dimemsion in dimensionList:
#     # isSucceed = False
#     runtimeList = []
#     # while not isSucceed or len(runtimeList) <= 3:
#     while len(runtimeList) <= 3:
#         isSucceed, runtime = mainAlgorithm(outputDirectory= outputDirectory, pointDimension=dimemsion, numOfPoint=
#     20, runCount=len(runtimeList))
#         # if isSucceed:
#         runtimeList.append(runtime)
#     dimensionRunTimeList.append(sum(runtimeList)/len(runtimeList))
#
# for pointNum in pointNumList:
#     # isSucceed = False
#     runtimeList = []
#     # while not isSucceed or len(runtimeList) <= 10:
#     while len(runtimeList) <= 3:
#         isSucceed, runtime = mainAlgorithm(outputDirectory=outputDirectory, pointDimension=2, numOfPoint=pointNum,
#                                            runCount=len(runtimeList))
#         # if isSucceed:
#         runtimeList.append(runtime)
#     pointNumRunTimeList.append(sum(runtimeList)/len(runtimeList))

# # For Debug Purpose:::::::###########
# for pointNum in pointNumList:
#     isSucceed = False
#     runtimeList = []
#     while len(runtimeList) <= 10:
#
#         isSucceed, runtime = mainAlgorithm(outputDirectory=outputDirectory, pointDimension=2, numOfPoint=pointNum,
#                                            runCount=len(runtimeList))
#         runtimeList.append(runtime)
#     pointNumRunTimeList.append(sum(runtimeList)/len(runtimeList))

# fig = plt.figure()
# plt.plot( dimensionList , dimensionRunTimeList)
# plt.savefig(os.path.join(outputDirectory, "Dimension_VS_Runtime.png"))
# plt.close(fig)
#
# fig = plt.figure()
# plt.plot( pointNumList , pointNumRunTimeList)
# plt.savefig(os.path.join(outputDirectory, "PointNum_VS_Runtime.png"))
# plt.close(fig)

isSucceed, runtime = mainAlgorithm(outputDirectory= outputDirectory, pointDimension=2, numOfPoint=
    20)