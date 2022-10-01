import enum

# enum for object types
class ObjType(enum.Enum):
    undefined = -1
    noDetection = 0
    truck = 1
    car = 2
    motorbike = 3
    bicycle = 4
    pedestrian = 5
    carOrTruck = 6