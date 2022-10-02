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

class WarnType(enum.Enum):
    NoWarning = 0    # No warning
    Overtake = 1     # Watch out, others are overtaking you!                           DONE
    FrontClose = 2   # You are getting too close to a vehicle in front of you!         DONE
    RearClose = 3    # A vehicle behind you is getting too close!                      DONE
    Blindspot = 4    # There may be vehicles/pedestrians/a cyclist in your blindspot!  DONE
    Cyclist = 5      # Be careful, there is a cyclist in front of you!                 DONE

warn_text = {
    WarnType.NoWarning: "No warning",
    WarnType.Overtake: "Watch out, someone is overtaking you!",
    WarnType.FrontClose: "You are getting too close to a vehicle in front of you!",
    WarnType.RearClose: "A vehicle behind you is getting too close!",
    WarnType.Blindspot: "There may be objects in your blindspot!",
    WarnType.Cyclist: "Be careful, there is a cyclist in front of you!"
}

warn_timeouts = {
    WarnType.NoWarning: 0,
    WarnType.Overtake: 0,
    WarnType.FrontClose: 0,
    WarnType.RearClose: 0,
    WarnType.Blindspot: 0,
    WarnType.Cyclist: 0
}