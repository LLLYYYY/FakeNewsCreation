class Hyperplane:

    hyperPlaneEquation = []
    pointList = []
    pointScribed = []
    maximumPointNumber = 0
    upperPointNumber = 0
    lowerPointNumber = 0
    onLinePointNumber = 0
    l2Norm = 0
    M = 0
    def __init__(self, hyperPlaneEquation, pointList, pointSide = [], maximumPointNumber = 0,
                  upperPointNumber = 0, lowerPointNumber = 0, onLinePointNumber = 0, M = 0, l2Norm = 0):
        self.hyperPlaneEquation = hyperPlaneEquation
        self.pointList = pointList
        self.maximumPointNumber = maximumPointNumber
        self.upperPointNumber = upperPointNumber
        self.lowerPointNumber = lowerPointNumber
        self.onLinePointNumber = onLinePointNumber
        self.l2Norm = l2Norm
        self.pointScribed = pointSide
        self.M = 0
