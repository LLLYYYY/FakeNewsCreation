import sys
sys.path.append('/opt/aci/sw/cplex/12.8.0/cplex/python/2.7/x86-64_linux')  # For server usage.

from Multi_Dimension import *
from HyperplaneConversion import *
from config import *
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import os
import timeit
from cplex.exceptions.errors import *
plt.switch_backend('agg')
plt.rcParams['figure.figsize'] = (10.0, 8.0)
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.dpi'] = 300

def mainAlgorithm(outputDirectory, pointDimension, numOfComsumerPoints,numberOfStoryVectors, ci, runCount = 0):
    """Parameter input: Output parameter. Return run time."""
    #Already changed to storyVector hyperplane calculation.

    functionStartTime = timeit.default_timer()
    outputDirectory = os.path.join(outputDirectory, str(pointDimension)+"D"+str(numOfComsumerPoints)+"P")
    if not os.path.isdir(outputDirectory):
        os.mkdir(outputDirectory)
    outputDirectory = os.path.join(outputDirectory, str(runCount))
    if not os.path.isdir(outputDirectory):
        os.mkdir(outputDirectory)

    consumerPointList = []
    storyVectorList = []
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
    whileCounter = 0
    while len(minimumDefenderUtilityList) <= 1 or ( len(minimumDefenderUtilityList) > 1 and abs(minimumDefenderUtilityList[-1] -
                                                                               minimumDefenderUtilityList[-2]) >
                                                    epsilon and whileCounter <= 100):

        whileCounter += 1

        originalConvertedHyperplaneMatchList = []  # Used to store original and converted list. The element of the list is
        # matched hyperplane pairs.

        print("Running dimension " + str(pointDimension)+ " with point number: "+ str(numOfComsumerPoints))
        # print("The Unbiased story vector is " + str(unbiasedStoryHyperplane.hyperPlaneEquation))

        plotOutputDirectory = os.path.join(outputDirectory, str(iter))
        if not os.path.isdir(plotOutputDirectory):
            os.mkdir(plotOutputDirectory)

        iterRange = [i for i in range(numOfComsumerPoints)]
        allComb = combinations(iterRange, pointDimension)
        for comb in allComb:
            pointListUsedToGenerateHyperplane = []
            for i in comb:
                pointListUsedToGenerateHyperplane.append(consumerPointList[i])
            #perturb the point list. Will work only for 2D
            #TODO: Fix for N dimensions
            pointListUsedToGenerateHyperplane[0] = [pointListUsedToGenerateHyperplane[0][0]+ 0.001, pointListUsedToGenerateHyperplane[0][1]+0.001]
            pointListUsedToGenerateHyperplane[1] = [pointListUsedToGenerateHyperplane[1][0]- 0.001, pointListUsedToGenerateHyperplane[1][1]-0.001]

            hyperplaneList.append(getHyperplaneEquation(pointListUsedToGenerateHyperplane))
        print("Finished getting hyperplane list. The size of the list is " + str(len(hyperplaneList)) + ".")

        hyperplaneList = getOriginalHyperplaneListWithUtilities2(hyperplaneList, consumerPointList,
                                                unbiasedStoryHyperplane.hyperPlaneEquation)

        #for hyperplane in hyperplaneList:
        #    print(hyperplane.pointSubscription)

        print("Finished Getting Lines with Utilities")
        #debug
        iterRange = [i for i in range(numOfComsumerPoints)]
        allComb = combinations(iterRange, pointDimension)
        #debug
        counter=0
        for hyperplane in hyperplaneList:
            #debug
            comb_counter=0
            for comb in allComb:
                if (comb_counter==counter):
                    # print("Current combination of points being considered: ")
                    for nv in comb:
                        # print(consumerPointList[nv])
                        pass
                    break
                comb_counter=comb_counter+1

            counter=counter+1

            #print(hyperplane.pointSubscription)
            #print(hyperplane.hyperPlaneEquation)
            for v in consumerPointList:
                # print(v)
                debugsinglePointSubscribeOfHyperplane2(hyperplane, v, ci)
            #debug
            try:
                convertedHyperplane = hyperPlaneConversion(hyperplane, consumerPointList, storyVectorList)
                originalConvertedHyperplaneMatchList.append([hyperplane, convertedHyperplane])
            except CplexSolverError as e:
                # print("Failed to generated hyperplane.")
                # print("Error message: " + str(e) + "\n\n\n\n\n\n\n\n\n")
                continue

        print("Finished converting hyperplanes.  The size of the convert hyperplanelist is:" + str(len(
            originalConvertedHyperplaneMatchList)) + ".")


        #The function will make sure mi is the same. Also, mi calculate is bigger than ci
        # not 0,
        try:
            hyperplaneList = getConvertedHyperplaneListWithUtilities(originalConvertedHyperplaneMatchList,
                                                                 consumerPointList, unbiasedStoryHyperplane.hyperPlaneEquation, ci)
        except ValueError as e:
            functionEndTime = timeit.default_timer()
            print("Error getting converted Hyperplane. Error Message: " + str(e))
            return False, functionEndTime - functionStartTime
        print("Finished generating converted hyperplane with utilities.")




        # Now plot the original and converted hyperplane.
        plotOriginalHyperplaneList = []
        plotConvertedHyperplaneList = []
        if len(originalConvertedHyperplaneMatchList) < 3:
            print("Failed to convert enough hyperplane.")
            #TODO: Should raise an error.
            break
        for p in range(3):
            matchedHyperplane = originalConvertedHyperplaneMatchList[p]
            plotOriginalHyperplaneList.append(matchedHyperplane[0])
            plotConvertedHyperplaneList.append(matchedHyperplane[1])
        plotHyperplaneList(consumerPointList, plotOriginalHyperplaneList, unbiasedStoryHyperplane,
                           plotOutputDirectory, "original hyperplane with consumer points", "figure1.png")
        plotHyperplaneList(consumerPointList, plotConvertedHyperplaneList, unbiasedStoryHyperplane,
                           plotOutputDirectory, "converted hyperplane with consumer points", "figure2.png")

        print("Finished printing the original and converted hyperplane charts.")

        # # After regenerating the hyperplane. Needs to recalculate the L2Norm.
        # getHyperplaneListWithUtilities(hyperplaneList, consumerPointList, unbiasedStoryHyperplane.hyperPlaneEquation,
        #                                inputStoryVector=storyVectorList, ci=ci)
        #
        # print("Finished Getting Lines with Utilities No2")

        hyperplaneList.sort(key=lambda pair: pair.defenderUtility)
        print("Finished Sorting Lines.")



        #Find the best strategy for adversary.
        adversaryHyperplane = Hyperplane([], [])
        defenderHyperplane = Hyperplane([], [])
        for hyperplane in hyperplaneList:
            if hyperplane.adversaryUtility > adversaryHyperplane.adversaryUtility:
                adversaryHyperplane = hyperplane


        print("Finished finding the best strategy for adversary")

        # Print the original graph.
        if pointDimension == 2:
            plotDefAdvHyperplane(consumerPointList, hyperplaneList[0].hyperPlaneEquation,
                                 adversaryHyperplane.hyperPlaneEquation,
                                 unbiasedStoryHyperplane.hyperPlaneEquation, plotOutputDirectory, "The Defender and "
                                                                                                  "the Adversary "
                                                                                                  "preference "
                                                                                                  "hyperplane",
                                 "figure3.png")

        # Now iterate the hyperplane list and try to move points.
        isFound = False
        for i in range(len(hyperplaneList)):
            if hyperplaneList[i].hyperPlaneEquation == adversaryHyperplane.hyperPlaneEquation:
                print("The defender hyperplane and the adversary hyperplane matched. List number: " + str(i))
                isFound = False
                break

            #TODO: FIX MOVE POINTS.
            isSucceed, movedPointList, defenderMaximumSubscription = movePoints(hyperplaneList[i],
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
                isFound = True
                if movedPointList == consumerPointList:
                    print("Points not moving.")
                    raise Exception("Points not moving. But the code should not reach this point. Error.")

                print("Found defender hyperplane " + str(i) + " that can do better than adversary hyperplane. \n" +
                      "The Defender maximum point count is " + str(defenderMaximumSubscription) + "\n")

                defenderHyperplane = hyperplaneList[i]

                # # For Debug purpose.
                #print(hyperplaneList[0].defenderUtility,  hyperplaneList[1].defenderUtility, hyperplaneList[2].defenderUtility)
                #print(hyperplaneList[i].defenderUtility)
                #print(hyperplaneList[-1].defenderUtility)

                if pointDimension == 2:
                    plotDefAdvHyperplane(consumerPointList, defenderHyperplane.hyperPlaneEquation,
                                         adversaryHyperplane.hyperPlaneEquation, unbiasedStoryHyperplane.hyperPlaneEquation,
                                         plotOutputDirectory, "The defender hyperplane that can do better than the "
                                                              "adversary one",
                                         "figure4.png")

                consumerPointList = movedPointList

                if pointDimension == 2:
                    plotDefAdvHyperplane(consumerPointList, defenderHyperplane.hyperPlaneEquation,
                                         adversaryHyperplane.hyperPlaneEquation, unbiasedStoryHyperplane.hyperPlaneEquation,
                                         plotOutputDirectory, "The defender and adversary hyperplane with moved "
                                                              "points" ,"figure5.png")
                break

        plt.show()
        print("Finished Printing Charts.")

        smallestL2Norm = defenderHyperplane.defenderUtility

        print("Current minimum defender utility is " + str(smallestL2Norm) + ".\n\n\n")


        #TODO: Will cause bugs. NOT sure why.
        # if movedPointList == originalConsumerPointList:
        #     functionEndTime = timeit.default_timer()
        #     return False, (functionEndTime - functionStartTime)

        iter += 1
        minimumDefenderUtilityList.append(smallestL2Norm)
        adversaryMaximumUtilityList.append(defenderHyperplane.adversaryUtility)
        if isFound == False:
            break
        #end outer while loop.

    functionEndTime = timeit.default_timer()

    fig = plt.figure()
    plt.plot([iteration + 1 for iteration in range(iter)], minimumDefenderUtilityList)
    plt.xlabel("Iteration of moved points and defender lists.")
    plt.ylabel("The Defender Utilities of Defender Hyperplane. (L2Norm)")
    plt.title("Iter_VS_DefU")
    plt.savefig(os.path.join(outputDirectory, "Iter_VS_Def.png"))
    plt.close(fig)

    fig = plt.figure()
    plt.plot([iteration + 1 for iteration in range(iter)], adversaryMaximumUtilityList)
    plt.xlabel("Iteration of moved points and defender lists.")
    plt.ylabel("The Adversary Utilities of Defender Hyperplane.(Point subscriptions)")
    plt.title("Iter_VS_AdvU")
    plt.savefig(os.path.join(outputDirectory, "Iter_VS_Adv.png"))
    plt.close(fig)

    return True, (functionEndTime - functionStartTime)

def plotDefAdvHyperplane(pointList, defenderHyperplaneEquation, adversaryHyperplaneEquation,
                         unbiasedStoryEquation, plotOutputDirectory, title, plotFileName):
    """Attension: Only works in two dimension..."""
    if not pointList:
        if len(pointList[0]) != 2:
            return

    fig = plt.figure()
    plt.scatter(*zip(*pointList))
    defenderPlotLineX = [-1, 1]
    adversaryPlotLineX = [-1, 1]
    unbiasedStoryVectorPlotLineX = [-1,1]

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
    unbiasedStoryVectorPlotLiney = [
        unbiasedStoryEquation[0] / unbiasedStoryEquation[1] - unbiasedStoryEquation[
            2] / unbiasedStoryEquation[1],
        -unbiasedStoryEquation[0] / unbiasedStoryEquation[1] - unbiasedStoryEquation[
            2] / unbiasedStoryEquation[1]]

    defenderPlot, = plt.plot(defenderPlotLineX, defenderPlotLineY)
    adversaryPlot, = plt.plot(adversaryPlotLineX, adversaryPlotLineY)
    unbiasedStoryVectorPlot, = plt.plot(unbiasedStoryVectorPlotLineX, unbiasedStoryVectorPlotLiney)
    plt.legend([defenderPlot, adversaryPlot, unbiasedStoryVectorPlot], ["Defender Hyperplane", "Adversary "
                                                                                               "Hyperplane",
                                                                        "Unbiased Story Vector"])


    plt.xlim(-1.5,1.5)
    plt.ylim(-1.5,1.5)
    plt.xlabel("x axis in the coordinate system")
    plt.ylabel("y axis in the coordinate system")
    plt.title(title)
    plt.savefig(os.path.join(plotOutputDirectory, plotFileName))
    plt.close(fig)

    return

def plotHyperplaneList(pointList, hyperplaneList, unbiasedStoryHyperplane, plotOutputDirectory, title, plotFileName):
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

    unbiasedStoryEquation = unbiasedStoryHyperplane.hyperPlaneEquation
    plotLineListX.append([-1, 1])
    plotLineListY.append([unbiasedStoryEquation[0] / unbiasedStoryEquation[1] - unbiasedStoryEquation[
        2] / unbiasedStoryEquation[1], -unbiasedStoryEquation[0] / unbiasedStoryEquation[1] -
                          unbiasedStoryEquation[
                              2] / unbiasedStoryEquation[1]])
    plots = []
    for i in range(len(plotLineListX)):
        plot, = plt.plot(plotLineListX[i],plotLineListY[i])
        plots.append(plot)
    plt.xlim(-1.5, 1.5)
    plt.ylim(-1.5, 1.5)
    plt.xlabel("x axis in the coordinate system")
    plt.ylabel("y axis in the coordinate system")
    plt.title(title)
    plt.legend(plots, ["First Hyperplane", "Second Hyperplane", "Third Hyperplane", "Unbiased Story Vector"])
    plt.savefig(os.path.join(plotOutputDirectory, plotFileName))
    plt.close(fig)

    return

# Run
dimensionRunTimeList = []
pointNumRunTimeList = []

outputDirectory = sys.argv[1]
#outputDirectory = ("/Users/auy212-admin/Downloads/FakeNewsOutput")
if not os.path.isdir(outputDirectory):
    raise Exception("Output Directory not accessible.")

# for dimemsion in dimensionList:
#     # isSucceed = False
#     runtimeList = []
#     # while not isSucceed or len(runtimeList) <= 3:
#     while len(runtimeList) <= 3:
#         isSucceed, runtime = mainAlgorithm(outputDirectory= outputDirectory, pointDimension=dimemsion,
#                                            numOfComsumerPoints=20, numberOfStoryVectors=50, ci = ci, runCount=len(
#             runtimeList))
#         # if isSucceed:
#         runtimeList.append(runtime)
#     dimensionRunTimeList.append(sum(runtimeList)/len(runtimeList))

for pointNum in consumerTotalPointNumberList:
    # isSucceed = False
    runtimeList = []
    # while not isSucceed or len(runtimeList) <= 10:
    while len(runtimeList) <= maximumRunCountForEachSituation:
        isSucceed, runtime = mainAlgorithm(outputDirectory=outputDirectory, pointDimension=2, numOfComsumerPoints
        =pointNum, numberOfStoryVectors= numberOfStoryVectors, ci=ci,
                                           runCount=len(runtimeList))
        if isSucceed:
            runtimeList.append(runtime)
    pointNumRunTimeList.append(sum(runtimeList)/len(runtimeList))

print(pointNumRunTimeList)
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