"""This file store all the global variables used in the program."""
from multiprocessing import  cpu_count


storyVectorNumber = 150
consumerPointNumber = 150


dimensionList = [2]   #Must be a list!!!
consumerTotalPointNumberList = [30]  #Must be a list!!!
numberOfStoryVectors = 150


# For equation to convert the hyperplane.
k = 3
ci = 0.1
e = 0.00001
M = 100000

precisionError=1e-10

maximumRunCountForEachSituation = 20

epsilon = 0.01  # Use for determine the minimum l2norm change.

longestMovingDistance = 0.4
singleTimeMovingDistance = 0.2

program_process_number = 4