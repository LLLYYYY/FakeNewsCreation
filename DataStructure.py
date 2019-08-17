import numpy as np

class Hyperplane:

    hyperPlaneEquation = np.array([0])
    pointSubscription = np.array([0])
    defenderUtility = 0
    adversaryUtility = 0
    def __init__(self, hyperPlaneEquation = np.array([0]), pointSubscription = np.array([0]), defenderUtility = 0,
                 adversaryUtility = 0):

        self.hyperPlaneEquation = hyperPlaneEquation
        self.pointSubscription = pointSubscription
        self.defenderUtility = defenderUtility
        self.adversaryUtility = adversaryUtility
