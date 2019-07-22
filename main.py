from Multi_Dimension import *
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

def main():
    pointDimension = 2
    pointList = []
    pointNumber = 1000

    unbiasedStoryVector = []
    storyPointList = []
    storyVectorNumber = 50
    hyperplaneList = []
    smallestNormLine = []

    for i in range(pointNumber):
        pointList.append(np.random.ranf(pointDimension).tolist())

    for i in range(storyVectorNumber):
        n = np.random.ranf(pointDimension).tolist()
        storyPointList.append(n)

    # print(pointList)
    meanStoryPoint = getMeanStoryPoint(storyPointList)
    unbiasedStoryVector = getHyperplaneEquation([meanStoryPoint,[-0.000001,-0.000001]])
    print("The Unbiased story vector is " + str(unbiasedStoryVector.hyperPlaneEquation))

    iterRange = [i for i in range(pointNumber)]
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
        fig = plt.subplot(2, 2, 1)
        plt.scatter(*zip(*pointList))
        defenderPlotLineX, defenderPlotLineY = zip(*hyperplaneList[0].pointList)
        adversaryPlotLineX, adversaryPlotLineY = zip(*adversaryHyperplane.pointList)
        # fig.set_xlim(left=-1, right=2)
        # fig.set_ylim(bottom=-1, top=2)
        plt.plot(defenderPlotLineX,defenderPlotLineY)
        plt.plot(adversaryPlotLineX,adversaryPlotLineY)

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
            print("Found defender hyperplane "+ str(i) + " that can do better than adversary hyperplane. \n" +
                  "The Defender maximum point count is " + str(defenderMaximumPoint) + "\n" +
                  "The Adversary maximum point count is " + str(adversaryMaximumPoint) + ".\n")

            # # For Debug purpose.
            # print(hyperplaneList[0].l2Norm,  hyperplaneList[1].l2Norm, hyperplaneList[2].l2Norm)
            # print(hyperplaneList[i].l2Norm)
            # print(hyperplaneList[-1].l2Norm)

            if pointDimension == 2:
                fig = plt.subplot(2, 2, 2)
                plt.scatter(*zip(*pointList))
                defenderPlotLineX, defenderPlotLineY = zip(*hyperplaneList[i].pointList)
                adversaryPlotLineX, adversaryPlotLineY = zip(*adversaryHyperplane.pointList)
                # fig.set_xlim(left=-1, right=2)
                # fig.set_ylim(bottom=-1, top=2)
                plt.plot(defenderPlotLineX, defenderPlotLineY)
                plt.plot(adversaryPlotLineX, adversaryPlotLineY)

            pointList = movedPointList

            if pointDimension == 2:
                fig = plt.subplot(2, 2, 3)
                plt.scatter(*zip(*pointList))
                defenderPlotLineX, defenderPlotLineY = zip(*hyperplaneList[i].pointList)
                adversaryPlotLineX, adversaryPlotLineY = zip(*adversaryHyperplane.pointList)
                # fig.set_xlim(left=-1, right=2)
                # fig.set_ylim(bottom=-1, top=2)
                plt.plot(defenderPlotLineX, defenderPlotLineY)
                plt.plot(adversaryPlotLineX, adversaryPlotLineY)

            break



    plt.show()
    print("Finished Printing Charts.")

# Run
main()