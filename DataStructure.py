class Hyperplane:

    hyperPlaneEquation = []
    pointSubscription = []
    defenderUtility = 0
    adversaryUtility = 0
    def __init__(self, hyperPlaneEquation, pointSubscription = [], defenderUtility = 0,
                 adversaryUtility = 0):
        self.hyperPlaneEquation = hyperPlaneEquation
        self.pointSubscription = pointSubscription
        self.defenderUtility = defenderUtility
        self.adversaryUtility = adversaryUtility
