from Multi_Dimension import *
from HyperplaneConversion import *
from config import *
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import sys
import os
import timeit
from cplex.exceptions.errors import *
plt.switch_backend('agg')

def mainAlgorithm(outputDirectory, pointDimension, numOfComsumerPoints,numberOfStoryVectors, runCount = 0) -> (
        bool, int):
    """Parameter input: Output parameter. Return run time."""
    #Already changed to storyVector hyperplane calculation.

    functionStartTime = timeit.default_timer()
    outputDirectory = os.path.join(outputDirectory, str(pointDimension)+"D"+str(numOfComsumerPoints)+"P")
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
    minimumDefenderUtilityList = []
    adversaryMaximumUtilityList = []
    adversaryMaximumUtility = 0

    iter = 0  # Used to distinguish different iterations of the same consumer point number and dimension.

    for i in range(numOfComsumerPoints):
        consumerPointList.append([ 2*x-1 for x in np.random.ranf(pointDimension).tolist()])
    originalConsumerPointList = consumerPointList

    for i in range(numberOfStoryVectors):
        storyVectorList.append([ 2*x-1 for x in np.random.ranf(pointDimension).tolist()])
    unbiasedStoryHyperplane = getMeanHyperplane(storyVectorList)

    while len(minimumDefenderUtilityList) <= 1 or ( len(minimumDefenderUtilityList) > 1 and abs(minimumDefenderUtilityList[-1] -
                                                                               minimumDefenderUtilityList[-2]) >
                                                    epsilon): # Cannot delete minimum defender utility list > 1. Will
        # cause crash.

        originalConvertedHyperplaneMatchList = []  # Used to store original and converted list. The element of the list is
        # matched hyperplane pairs.

        print("Running dimension " + str(pointDimension)+ " with point number: "+ str(numOfComsumerPoints))
        print("The Unbiased story vector is " + str(unbiasedStoryHyperplane.hyperPlaneEquation))

        plotOutputDirectory = os.path.join(outputDirectory, str(iter))
        if not os.path.isdir(plotOutputDirectory):
            os.mkdir(plotOutputDirectory)

        iterRange = [i for i in range(numOfComsumerPoints)]
        allComb = combinations(iterRange, pointDimension)
        for comb in allComb:
            pointListUsedToGenerateHyperplane = []
            for i in comb:
                pointListUsedToGenerateHyperplane.append(consumerPointList[i])
            hyperplaneList.append(getHyperplaneEquation(pointListUsedToGenerateHyperplane))
        print("Finished getting hyperplane list. The size of the list is " + str(len(hyperplaneList)) + ".")

        getHyperplaneListWithUtilities(hyperplaneList, consumerPointList, unbiasedStoryHyperplane.hyperPlaneEquation,
                                       inputStoryVector=storyVectorList, ci = ci)

        print("Finished Getting Lines with Utilities")

        convertedHyperplaneList = []
        for hyperplane in hyperplaneList:
            try:
                convertedHyperplane = hyperPlaneConversion(hyperplane, consumerPointList, storyVectorList)
                convertedHyperplaneList.append(convertedHyperplane)
                originalConvertedHyperplaneMatchList.append([hyperplane, convertedHyperplane])
            except CplexSolverError as e:
                print("\n\n\n\n\n\n\n\n Failed to generated hyperplane.")
                print("Error message: " + str(e) + "\n\n\n\n\n\n")
                continue

        print("Finished converting hyperplanes.  The size of the convert hyperplanelist is:" + str(len(
            convertedHyperplaneList)) + ".")

        hyperplaneList = convertedHyperplaneList

        #TODO: PLEASE CHECK m_i values match
        #TODO: make sure to check mi and see if it is the same. Also, mi calculate should be bigger than ci not 0,
        # with converted hyperplanes.
        getHyperplaneListWithUtilities(hyperplaneList, consumerPointList, unbiasedStoryHyperplane.hyperPlaneEquation,
                                       inputStoryVector=storyVectorList, ci=ci)
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
        plotHyperplaneList(consumerPointList, plotOriginalHyperplaneList, plotOutputDirectory, "figure1.png")
        plotHyperplaneList(consumerPointList, plotConvertedHyperplaneList, plotOutputDirectory, "figure2.png")

        print("Finished printing the original and converted hyperplane charts.")

        # # After regenerating the hyperplane. Needs to recalculate the L2Norm.
        # getHyperplaneListWithUtilities(hyperplaneList, consumerPointList, unbiasedStoryHyperplane.hyperPlaneEquation,
        #                                inputStoryVector=storyVectorList, ci=ci)
        #
        # print("Finished Getting Lines with Utilities No2")

        hyperplaneList.sort(key=lambda pair: pair.l2Norm)
        print("Finished Sorting Lines.")


        #TODO: Added adversary utilities. Should be M inside the hyperplane class. But decided by >= ci.
        #Find the best strategy for adversary.
        adversaryHyperplane = Hyperplane([], [])
        defenderHyperplane = Hyperplane([], [])
        for hyperplane in hyperplaneList:
            if hyperplane.maximumPointNumber > adversaryHyperplane.maximumPointNumber:
                adversaryHyperplane = hyperplane


        print("Finished finding the best strategy for adversary")

        # Print the original graph.
        if pointDimension == 2:
            plotDefAdvHyperplane(consumerPointList, hyperplaneList[0].hyperPlaneEquation,
                                 adversaryHyperplane.hyperPlaneEquation, plotOutputDirectory, "figure3.png")

        # Now iterate the hyperplane list and try to move points.
        for i in range(len(hyperplaneList)):
            if hyperplaneList[i] == adversaryHyperplane:
                print("The defender hyperplane and the adversary hyperplane matched. List number: " + str(i))
                break

            #TODO: FIX MOVE POINTS.
            isSucceed, movedPointList, defenderMaximumPoint, adversaryMaximumUtility = movePoints(hyperplaneList[i],
                                                                                                     adversaryHyperplane,

                                                                                     consumerPointList, originalConsumerPointList,
                                                                                                ci=ci)

            # if i == len(hyperplaneList) - 2: # For testing and visualization purpose.
            #     print("Debug ploting mode.")
            #     temPointList = movedPointList
            #     if pointDimension == 2:
            #         fig = plt.subplot(2, 2, 3)
            #         plt.scatter(*zip(*temPointList))
            #         defenderPlotLineX, defenderPlotLineY = zip(*hyperplaneList[i].consumerPointList)
            #         adversaryPlotLineX, adversaryPlotLineY = zip(*adversaryHyperplane.consumerPointList)
            #         # fig.set_xlim(left=-1, right=2)
            #         # fig.set_ylim(bottom=-1, top=2)
            #         plt.plot(defenderPlotLineX, defenderPlotLineY)
            #         plt.plot(adversaryPlotLineX, adversaryPlotLineY)
            #     break

            if isSucceed == False:
                continue
            else:
                if movedPointList == consumerPointList:
                    print("Points not moving.")
                    raise Exception("Points not moving. But the code should not reach this point. Error.")

                print("Found defender hyperplane " + str(i) + " that can do better than adversary hyperplane. \n" +
                      "The Defender maximum point count is " + str(defenderMaximumPoint) + "\n" +
                      "The Adversary maximum point count is " + str(adversaryMaximumUtility) + ".")

                defenderHyperplane = hyperplaneList[i]

                # # For Debug purpose.
                # print(hyperplaneList[0].l2Norm,  hyperplaneList[1].l2Norm, hyperplaneList[2].l2Norm)
                # print(hyperplaneList[i].l2Norm)
                # print(hyperplaneList[-1].l2Norm)

                if pointDimension == 2:
                    plotDefAdvHyperplane(consumerPointList, defenderHyperplane.hyperPlaneEquation,
                                         adversaryHyperplane.hyperPlaneEquation, plotOutputDirectory, "figure4.png")

                consumerPointList = movedPointList

                if pointDimension == 2:
                    plotDefAdvHyperplane(consumerPointList, defenderHyperplane.hyperPlaneEquation,
                                         adversaryHyperplane.hyperPlaneEquation, plotOutputDirectory, "figure5.png")
                break

        plt.show()
        print("Finished Printing Charts.")

        smallestL2Norm = defenderHyperplane.l2Norm

        print("Current minimum defender utility is " + str(smallestL2Norm) + ".\n\n\n")


        #TODO: Will cause bugs. NOT sure why.
        # if movedPointList == originalConsumerPointList:
        #     functionEndTime = timeit.default_timer()
        #     return False, (functionEndTime - functionStartTime)

        iter += 1
        minimumDefenderUtilityList.append(smallestL2Norm)
        adversaryMaximumUtilityList.append(adversaryMaximumUtility)
        #end outer while loop.

    functionEndTime = timeit.default_timer()

    fig = plt.figure()
    plt.plot([iteration + 1 for iteration in range(iter)], minimumDefenderUtilityList)
    plt.savefig(os.path.join(outputDirectory, "Iter_VS_Def.png"))
    plt.close(fig)

    fig = plt.figure()
    plt.plot([iteration + 1 for iteration in range(iter)], adversaryMaximumUtilityList)
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

    #TODO: Will crash if hyperplane's parameter at y axis equal to 0.
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
        # TODO: Will crash if hyperplane's parameter at y axis equal to 0.
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

dimensionRunTimeList = []
pointNumRunTimeList = []

outputDirectory = sys.argv[1]
if not os.path.isdir(outputDirectory):
    raise Exception("Output Directory not accessible.")

for dimemsion in dimensionList:
    # isSucceed = False
    runtimeList = []
    # while not isSucceed or len(runtimeList) <= 3:
    while len(runtimeList) <= 3:
        isSucceed, runtime = mainAlgorithm(outputDirectory= outputDirectory, pointDimension=dimemsion,
                                           numOfComsumerPoints=20, numberOfStoryVectors=50, runCount=len(runtimeList))
        # if isSucceed:
        runtimeList.append(runtime)
    dimensionRunTimeList.append(sum(runtimeList)/len(runtimeList))

for pointNum in consumerTotalPointNumberList:
    # isSucceed = False
    runtimeList = []
    # while not isSucceed or len(runtimeList) <= 10:
    while len(runtimeList) <= 3:
        isSucceed, runtime = mainAlgorithm(outputDirectory=outputDirectory, pointDimension=2, numOfComsumerPoints
        =pointNum, numberOfStoryVectors= 50,
                                           runCount=len(runtimeList))
        # if isSucceed:
        runtimeList.append(runtime)
    pointNumRunTimeList.append(sum(runtimeList)/len(runtimeList))

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

# isSucceed, runtime = mainAlgorithm(outputDirectory= outputDirectory, pointDimension=2, numOfComsumerPoints= 20,
                                   # numberOfStoryVectors=50)