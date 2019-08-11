class Hyperplane:

    hyperPlaneEquation = []
    pointSubscription = []
    defenderUtility = 0
    adversaryUtility = 0
    def __init__(self, hyperPlaneEquation, pointSubscription = [], defenderUtility = 0,
                 adversaryUtility = 0):
        # Change the normal vector to unit vector.
        meg = (sum([x ** 2 for x in hyperPlaneEquation[-1]])) ** 0.5
        if meg != 0:
            hyperPlaneEquation = [x/meg for x in hyperPlaneEquation]
        else:
            raise ValueError("Getting a all zeros hyperplane.")

        self.hyperPlaneEquation = hyperPlaneEquation
        self.pointSubscription = pointSubscription
        self.defenderUtility = defenderUtility
        self.adversaryUtility = adversaryUtility
