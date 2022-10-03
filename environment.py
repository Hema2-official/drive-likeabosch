from datasets import *
from common_types import *
import time

# timing variables
min_real_lifetime_typed = 2
min_real_lifetime_undef = 3.5
last_seen_kill_time = 1.5
type_time_threshold = 0.5

# sensor calue effect tuning
merge_avg_factor = 4

# safety distance & things tuning
front_nearby_threshold = 7
front_close_threshold = 4
rear_nearby_threshold = 4
side_nearby_threshold = 6
by_the_side_threshold = 3
min_overtake_speed = 5

class Environment():
    def __init__(self):
        self.temporary_objects = []
        self.objects = []
        self.delta_time = 0
        self.ref = None

    def update(self, obj_array, reference, delta_time):
        self.delta_time = delta_time
        self.ref = reference

        # update temporary objects
        for obj in self.temporary_objects:
            obj.vx += obj.ax * delta_time
            obj.vy += obj.ay * delta_time
            obj.dx += (obj.vx - self.ref.vx) * delta_time
            obj.dy += (obj.vy - self.ref.vy) * delta_time
            obj.last_seen += delta_time
        
        # update objects
        for obj in self.objects:
            obj.vx += obj.ax * delta_time
            obj.vy += obj.ay * delta_time
            obj.dx += obj.vx * delta_time
            obj.dy += obj.vy * delta_time
            obj.last_seen += delta_time

        # process camera objects
        for obj in obj_array.cam_objects:
            if (obj.dx < 1 and obj.dy < 1) or 3.5 > obj.dx > 3:
                continue
            if not self.process_nearby(self.objects, obj) and not self.process_nearby(self.temporary_objects, obj):
                self.temporary_objects.append(obj)

        # process radar objects
        radar_objs = obj_array.rad_a_objects + obj_array.rad_b_objects + obj_array.rad_c_objects + obj_array.rad_d_objects
        for obj in radar_objs:
            if (-0.8 < obj.dx < 0.8 and -0.8 < obj.dy < 0.8) or 3.5 > obj.dx > 3:
                continue
            if not self.process_nearby(self.objects, obj) and not self.process_nearby(self.temporary_objects, obj):
                self.temporary_objects.append(obj)
        
        # update temporary objects' states
        for obj in self.temporary_objects:
            if obj.type_time > type_time_threshold:
                obj.obj_type = obj.potential_type
                obj.potential_type = None
                obj.type_time = 0
            if obj.last_seen > min_real_lifetime_typed:
                self.temporary_objects.remove(obj)
                continue
            if obj.lifetime > min_real_lifetime_undef or (obj.lifetime > min_real_lifetime_typed and obj.obj_type != ObjType.undefined and obj.obj_type != None):
                self.objects.append(obj)
                self.temporary_objects.remove(obj)
                continue
            
        # update objects' states
        for obj in self.objects:
            if obj.type_time > type_time_threshold:
                obj.obj_type = obj.potential_type
                obj.potential_type = None
                obj.type_time = 0
            if obj.last_seen > last_seen_kill_time + obj.lifetime / 5:
                self.objects.remove(obj)
                continue

    def process_nearby(self, group, obj):
        # check if any object is nearby
        nearby = self.check_nearby(group, obj)
        if nearby is not None:
            # if so, merge them
            nearby.lifetime += self.delta_time
            nearby.last_seen = 0
            if obj.obj_type != ObjType.undefined and obj.obj_type != None:
                nearby.potential_type = obj.obj_type
                nearby.type_time += self.delta_time
            nearby.ax = obj.ax
            nearby.ay = obj.ay
            nearby.vx = obj.vx
            nearby.vy = obj.vy
            nearby.dx = (nearby.dx * merge_avg_factor + obj.dx) / (merge_avg_factor + 1)
            nearby.dy = (nearby.dy * merge_avg_factor + obj.dy) / (merge_avg_factor + 1)
            nearby.dz = (nearby.dz * merge_avg_factor + obj.dz) / (merge_avg_factor + 1)
            return True
        return False

    def check_nearby(self, group, obj):
        for other_obj in group:
            if obj == other_obj or obj.is_near(other_obj):
                return other_obj

        return None

    def check_safety(self):
        warnings = set()
        for obj in self.objects:
            # look for objects in front of the car
            if obj.dx > 0 and obj.dx < front_nearby_threshold and obj.dy < side_nearby_threshold and obj.dy > -side_nearby_threshold: # obj is in front of the car
                if obj.obj_type == ObjType.bicycle: # obj is a cyclist
                    warnings.add(WarnType.Cyclist)
                if obj.dx < front_close_threshold: # obj is too close
                    warnings.add(WarnType.FrontClose)
            
            # look for objects that are by the side of the car
            if by_the_side_threshold > obj.dx > -by_the_side_threshold:  # obj is by the side of the car
                if side_nearby_threshold > obj.dy > -side_nearby_threshold:   # obj is close to the side of the car
                    warnings.add(WarnType.Blindspot)

                if obj.vx > min_overtake_speed and side_nearby_threshold > obj.dy: # obj is moving faster than the car (on the left)
                    warnings.add(WarnType.Overtake)

            # look for objects in the rear of the car
            if obj.dx < 0 and obj.dx > -rear_nearby_threshold and obj.dy < side_nearby_threshold and obj.dy > -side_nearby_threshold: # obj is in the rear of the car
                warnings.add(WarnType.RearClose)
        return warnings
