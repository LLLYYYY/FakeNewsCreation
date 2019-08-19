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
from multiprocessing import Pool, cpu_count
from cplex.exceptions.errors import *
plt.switch_backend('agg')
plt.rcParams['figure.figsize'] = (10.0, 8.0)
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.dpi'] = 300

def mainAlgorithm(outputDirectory, pointDimension, numOfComsumerPoints,numberOfStoryVectors, ci, runCount = 0):
    """Parameter input: Output parameter. Return run time."""
    #Already changed to storyVector hyperplane calculation.

    functionStartTime = timeit.default_timer()
    outputDirectory = os.path.join(outputDirectory, str(runCount))
    if not os.path.isdir(outputDirectory):
        os.mkdir(outputDirectory)

    hyperplaneList = []
    minimumDefenderUtilityList = []
    adversaryMaximumUtilityList = []
    adversaryMaximumUtility = 0
    adversaryHyperplane = Hyperplane([], [])
    defenderHyperplane = Hyperplane([], [])

    iter = 0  # Used to distinguish different iterations of the same consumer point number and dimension.

    consumerPointList = np.random.rand(numOfComsumerPoints, pointDimension)
    consumerPointList = consumerPointList * 2 - 1
    originalConsumerPointList = np.copy(consumerPointList)

    storyVectorList = np.random.rand(numberOfStoryVectors, pointDimension)
    storyVectorList = storyVectorList * 2 - 1

    unbiasedStoryHyperplane = getMeanHyperplane(storyVectorList)

    whileCounter = 0
    while len(minimumDefenderUtilityList) <= 1 or ( len(minimumDefenderUtilityList) > 1 and abs(minimumDefenderUtilityList[-1] -
                                                                               minimumDefenderUtilityList[-2]) >
                                                    epsilon and whileCounter <= 100):

        whileCounter += 1

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
            pointListUsedToGenerateHyperplane[0] = [pointListUsedToGenerateHyperplane[0][0] + 0.001,
                                                    pointListUsedToGenerateHyperplane[0][1]+0.001]
            pointListUsedToGenerateHyperplane[1] = [pointListUsedToGenerateHyperplane[1][0] - 0.001,
                                                    pointListUsedToGenerateHyperplane[1][1]-0.001]
            # When changing into Hyperplane instance, the hyperplane equation will change into numpy.array.
            # For hyperplane list. Because the hyperplane instance is a custom type
            hyperplaneList.append(getHyperplaneEquation(pointListUsedToGenerateHyperplane))
        print("Finished getting hyperplane list. The size of the list is " + str(len(hyperplaneList)) + ".")

        hyperplaneList = getOriginalHyperplaneListWithUtilities(hyperplaneList, consumerPointList,
                                                                unbiasedStoryHyperplane.hyperPlaneEquation)
        originalHyperplaneList = hyperplaneList # Use for data storage.
        print("Finished Getting Lines with Utilities")

        cplexProcessPool = Pool(processes=program_process_number)
        cplexPoolResult = []
        for hyperplane in hyperplaneList:
            # convertedHyperplane = hyperPlaneConversion(hyperplane, consumerPointList, storyVectorList)
            cplexPoolResult.append(cplexProcessPool.apply_async(hyperPlaneConversion,
                                                                                     args= (hyperplane,
                                                                                            consumerPointList,
                                                                                            storyVectorList,)))
        cplexProcessPool.close()
        cplexProcessPool.join()

        originalConvertedHyperplaneMatchList = []
        for res in cplexPoolResult:
            originalConvertedHyperplaneMatchList.append(res.get())
        originalConvertedHyperplaneMatchList = [x for x in originalConvertedHyperplaneMatchList if x is not None] # Used to store original and converted list. The element
        # of the
        # list is
        # matched hyperplane pairs.

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
            return False, functionEndTime - functionStartTime, 0, [], []
        print("Finished generating converted hyperplane with utilities.")

        if whileCounter > 1 and defenderHyperplane != Hyperplane([], []) and adversaryHyperplane != Hyperplane([], []):
            hyperplaneList.append(defenderHyperplane)
            # hyperplaneList.append(adversaryHyperplane)

        # Now plot the original and converted hyperplane.
        plotOriginalHyperplaneList = []
        plotConvertedHyperplaneList = []
        if len(originalConvertedHyperplaneMatchList) < 3:
            print("Failed to convert enough hyperplane.")
            return False, 0, 0, [], []
        for p in range(3):
            matchedHyperplane = originalConvertedHyperplaneMatchList[p]
            plotOriginalHyperplaneList.append(matchedHyperplane[0])
            plotConvertedHyperplaneList.append(matchedHyperplane[1])
        plotHyperplaneList(consumerPointList, plotOriginalHyperplaneList, unbiasedStoryHyperplane,
                           plotOutputDirectory, "original hyperplane with consumer points", "figure1.png")
        plotHyperplaneList(consumerPointList, plotConvertedHyperplaneList, unbiasedStoryHyperplane,
                           plotOutputDirectory, "converted hyperplane with consumer points", "figure2.png")

        print("Finished printing the original and converted hyperplane charts.")

        # Save running data to csv files.
        # f = open(os.path.join(plotOutputDirectory, "consumerPlotList.csv"), 'wb')
        np.savetxt(os.path.join(plotOutputDirectory, "consumerPlotList.csv"), consumerPointList, delimiter=',')
        np.savetxt(os.path.join(plotOutputDirectory, "storyVectorList.csv"), storyVectorList, delimiter=',')

        f = open(os.path.join(plotOutputDirectory, "originalHyperplaneList.csv"), 'wb')
        for originalHyperplane in originalHyperplaneList:
            hyperplaneEquation = np.array([originalHyperplane.hyperPlaneEquation])
            np.savetxt(f, hyperplaneEquation, delimiter=',')
        f.close()

        f = open(os.path.join(plotOutputDirectory, "convertedHyperplaneList.csv"), 'wb')
        for convertedHyperplane in hyperplaneList:
            hyperplaneEquation = np.array([convertedHyperplane.hyperPlaneEquation])
            np.savetxt(f, hyperplaneEquation, delimiter=',')
        f.close()

        # # After regenerating the hyperplane. Needs to recalculate the L2Norm.
        # getHyperplaneListWithUtilities(hyperplaneList, consumerPointList, unbiasedStoryHyperplane.hyperPlaneEquation,
        #                                inputStoryVector=storyVectorList, ci=ci)
        #
        # print("Finished Getting Lines with Utilities No2")

        hyperplaneList.sort(key=lambda pair: pair.defenderUtility)
        print("Finished Sorting Lines.")



        #Find the best strategy for adversary.
        for hyperplane in hyperplaneList:
            if hyperplane.adversaryUtility >= adversaryHyperplane.adversaryUtility:
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
            if np.array_equal(hyperplaneList[i].hyperPlaneEquation, adversaryHyperplane.hyperPlaneEquation):
                print("The defender hyperplane and the adversary hyperplane matched. List number: " + str(i))
                isFound = False
                break

            #For Debug purpose. Make sure that the new l2norm will not be larger than the previous defender
            # hyperplane's l2norm.
            if np.array_equal(hyperplaneList[i].hyperPlaneEquation, defenderHyperplane.hyperPlaneEquation):
                print("The defender hyperplane and previous defender hyperplane matched. List number: " + str(i))
                isFound = False
                break

            isSucceed, movedPointList, defenderMaximumSubscription = movePoints(hyperplaneList[i],
                                                                                                     adversaryHyperplane,

                                                                                     consumerPointList, originalConsumerPointList,
                                                                                                ci=ci)

            if isSucceed == False:
                continue
            else:
                isFound = True
                if np.array_equal(movedPointList, consumerPointList):
                    print("Points not moving.")
                    raise Exception("Points not moving. But the code should not reach this point. Error.")

                print("Found defender hyperplane " + str(i) + " that can do better than adversary hyperplane. \n" +
                      "The Defender maximum point count is " + str(defenderMaximumSubscription) + "\n")

                defenderHyperplane.adversaryUtility = defenderMaximumSubscription
                defenderHyperplane = hyperplaneList[i]
                adversaryHyperplane = defenderHyperplane

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

        iter += 1
        minimumDefenderUtilityList.append(smallestL2Norm)
        adversaryMaximumUtilityList.append(defenderHyperplane.adversaryUtility)

        if smallestL2Norm > adversaryHyperplane.defenderUtility:
            raise Exception("The chosen defender hyperplane has larger L2Norm compare to the adversary hyperplane.")

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

    return True, (functionEndTime - functionStartTime), iteration+1, minimumDefenderUtilityList, adversaryMaximumUtilityList

def plotDefAdvHyperplane(pointList, defenderHyperplaneEquation, adversaryHyperplaneEquation,
                         unbiasedStoryEquation, plotOutputDirectory, title, plotFileName):
    """Only works in two dimension... Only works when the y axis parameter of the hyperplane not equals to 0."""
    if not len(pointList) == 0:
        if len(pointList[0]) != 2:
            return
    else:
        return

    if defenderHyperplaneEquation[1] == 0 or adversaryHyperplaneEquation[1] == 0 or unbiasedStoryEquation[1] == 0:
        print("The y axis parameter of the hyperplane equals to 0. Failed to plot.")
        return

    fig = plt.figure()
    plt.scatter(*zip(*pointList))
    defenderPlotLineX = [-1, 1]
    adversaryPlotLineX = [-1, 1]
    unbiasedStoryVectorPlotLineX = [-1,1]

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
    if not len(pointList) == 0:
        if len(pointList[0]) != 2:
            return
    else:
        return

    fig = plt.figure()
    plt.scatter(*zip(*pointList))
    plotLineListX = []
    plotLineListY = []
    for hyperplane in hyperplaneList:
        hyperplaneEquation = hyperplane.hyperPlaneEquation
        plotLineListX.append([-1,1])
        if hyperplaneEquation[1] == 0:
            print("The y axis parameter of the hyperplane equals to 0. Failed to plot.")
            return
        plotLineListY.append([hyperplaneEquation[0] / hyperplaneEquation[1] - hyperplaneEquation[
        2] / hyperplaneEquation[1], -hyperplaneEquation[0] / hyperplaneEquation[1] -
                         hyperplaneEquation[
                             2] / hyperplaneEquation[1]])
    unbiasedStoryEquation = unbiasedStoryHyperplane.hyperPlaneEquation
    if unbiasedStoryEquation[1] == 0:
        print("The y axis parameter of the hyperplane equals to 0. Failed to plot.")
        return
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

def unbalancedListPlus(listA, listB):
    outputList = []
    if len(listA) == 0:
        outputList = listB
    elif len(listB) == 0:
        outputList = listA
    elif len(listA) <= len(listB):
        for i in range(len(listA)):
            listB[i] += listA[i]
            outputList = listB
    elif len(listB) < len(listA):
        for i in range(len(listB)):
            listA[i] += listB[i]
            outputList = listA
    else:
        raise Exception("Logic error in unbalancedListPlus.")
    return outputList

# Run
dimensionRunTimeList = []
pointNumRunTimeList = []

outputDirectory = sys.argv[1]
#outputDirectory = ("/Users/auy212-admin/Downloads/FakeNewsOutput")
if not os.path.isdir(outputDirectory):
    raise Exception("Output Directory not accessible.")

iterationNumberList = []
adversaryUtilityList = []
defenderUtilityList = []
for pointNum in consumerTotalPointNumberList:

    currOutputDirectory = os.path.join(outputDirectory, str(2) + "D" + str(pointNum) + "P")
    if not os.path.isdir(currOutputDirectory):
        os.mkdir(currOutputDirectory)

    runtimeList = []
    aveDefUtilityList = []
    aveAdvUtilityList = []
    iterationCount = [] #Used for counting how many times the specific iteration goes through.
    while len(runtimeList) <= maximumRunCountForEachSituation:
        isSucceed, runtime, iteration, defU, advU = mainAlgorithm(outputDirectory=currOutputDirectory,
                                                                  pointDimension=2,
                                                                  numOfComsumerPoints=pointNum, numberOfStoryVectors= numberOfStoryVectors, ci=ci,
                                                                  runCount=len(runtimeList))
        if isSucceed:
            runtimeList.append(runtime)
            iterationNumberList.append(iteration)
            aveDefUtilityList = unbalancedListPlus(aveDefUtilityList, defU)
            aveAdvUtilityList = unbalancedListPlus(aveAdvUtilityList, advU)
            iterationCount = unbalancedListPlus(iterationCount, iteration * [1])

    pointNumRunTimeList.append(sum(runtimeList)/len(runtimeList))
    print(aveAdvUtilityList)
    print(aveDefUtilityList)
    print(iterationCount)
    aveDefUtilityList = [x/y for x,y in zip(aveDefUtilityList, iterationCount)]
    aveAdvUtilityList = [x/y for x,y in zip(aveAdvUtilityList, iterationCount)]

    fig = plt.figure()
    print(len(aveDefUtilityList))
    plt.plot([iter + 1 for iter in range(len(iterationCount))], aveDefUtilityList)
    plt.xlabel("Iteration")
    plt.ylabel("The average defender utilities in each iterations")
    plt.title("Iter_VS_AveDefU")
    plt.savefig(os.path.join(currOutputDirectory, "Iter_VS_AveDefU.png"))
    plt.close(fig)

    fig = plt.figure()
    plt.plot([iter + 1 for iter in range(len(iterationCount))], aveAdvUtilityList)
    plt.xlabel("Iteration")
    plt.ylabel("The average adversary utilities in each iterations")
    plt.title("Iter_VS_AveAdvU")
    plt.savefig(os.path.join(currOutputDirectory, "Iter_VS_AveAdvU.png"))
    plt.close(fig)

f = open(os.path.join(outputDirectory, "RuntimeData.txt"), 'aw')
for i in range(len(consumerTotalPointNumberList)):
    f.write("Point number: " + str(consumerTotalPointNumberList[i]) + ". Runtime: " + str(pointNumRunTimeList[i]) +
            ". Iteration Number: " + str(iterationCount) + ".\n")
f.close()
