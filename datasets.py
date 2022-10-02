import csv
from common_types import *

x_nearby_threshold = 5
y_nearby_threshold = 1.75

def load_csv(filename):
    with open(filename) as csv_file:
        reader = csv.reader(csv_file)
        return list(reader)

class RawObject:
    def __init__(self, ax, ay, dx, dy, dz, prob, vx, vy, obj_type = ObjType.undefined):
        self.obj_type = obj_type  # always present OR undefined
        self.ax = ax
        self.ay = ay
        self.dx = dx     # always present
        self.dy = dy     # always present
        self.dz = dz
        self.prob = prob
        self.vx = vx     # always present
        self.vy = vy     # always present
        self.lifetime = 0
        self.last_seen = 0
        self.potential_type = None
        self.type_time = 0

    def is_near(self, other_obj):
        return abs(self.dx - other_obj.dx) < x_nearby_threshold and abs(self.dy - other_obj.dy) < y_nearby_threshold


class ReferenceValues:
    def __init__(self, raw_data):
        self.timestamp = raw_data[0]
        self.ax = int(raw_data[1]) / 2048
        self.ay = int(raw_data[2]) / 2048
        self.yaw = int(raw_data[3]) / 16384
        self.vx = int(raw_data[5]) / 256
        self.vy = int(raw_data[6]) / 256

class ObjectArray:
    def __init__(self, raw_data):
        self.timestamp = raw_data[0]
        self.cam_timestamp = raw_data[1]
        self.cam_pos_x = float(raw_data[401]) / 256
        self.cam_pos_y = float(raw_data[402]) / 256
        self.cam_pos_z = float(raw_data[403]) / 256
        self.cam_objects = []
        for i in range(15):
            self.cam_objects.append(
                RawObject(
                    0,
                    0,
                    (int(raw_data[2 + i]) / 128) + self.cam_pos_x,    # dx, offset: 2
                    (int(raw_data[17 + i]) / 128) + self.cam_pos_y,   # dy, offset: 17
                    0,
                    1,
                    int(raw_data[47 + i]) / 256,   # vx, offset: 47
                    int(raw_data[62 + i]) / 256,   # vy, offset: 62
                    int(raw_data[32 + i])))        # obj_type, offset: 32

        self.rad_a_timestamp = raw_data[77]
        self.rad_b_timestamp = raw_data[78]
        self.rad_c_timestamp = raw_data[79]
        self.rad_d_timestamp = raw_data[80]
        self.rad_a_objects = []
        self.rad_b_objects = []
        self.rad_c_objects = []
        self.rad_d_objects = []
        for i in range(10):
            self.rad_a_objects.append(    # radar A, left front
                RawObject(
                    int(raw_data[i * 4 + 81]) / 2048,   # ax, offset: 81
                    int(raw_data[i * 4 + 121]) / 2048,  # ay, offset: 121
                    int(raw_data[i * 4 + 161]) / 128 + 3.4738,   # dx, offset: 161
                    int(raw_data[i * 4 + 201]) / 128 + 0.6286,   # dy, offset: 201
                    int(raw_data[i * 4 + 241]) / 128 + 0.5156,   # dz, offset: 241
                    int(raw_data[i * 4 + 281]) / 128,   # prob, offset: 281
                    int(raw_data[i * 4 + 321]) / 256,   # vx, offset: 321
                    int(raw_data[i * 4 + 361]) / 256))  # vy, offset: 361
            self.rad_b_objects.append(    # radar B, right front
                RawObject(
                    int(raw_data[i * 4 + 82]) / 2048,   # ax, offset: 82
                    int(raw_data[i * 4 + 122]) / 2048,  # ay, offset: 122
                    int(raw_data[i * 4 + 162]) / 128 + 3.4738,   # dx, offset: 162
                    int(raw_data[i * 4 + 202]) / 128  -0.6286,   # dy, offset: 202
                    int(raw_data[i * 4 + 242]) / 128 + 0.5156,   # dz, offset: 242
                    int(raw_data[i * 4 + 282]) / 128,   # prob, offset: 282
                    int(raw_data[i * 4 + 322]) / 256,   # vx, offset: 322
                    int(raw_data[i * 4 + 362]) / 256))  # vy, offset: 362
            self.rad_c_objects.append(    # radar C, left rear
                RawObject(
                    int(raw_data[i * 4 + 83]) / 2048,   # ax, offset: 83
                    int(raw_data[i * 4 + 123]) / 2048,  # ay, offset: 123
                    int(raw_data[i * 4 + 163]) / 128  -0.7664,   # dx, offset: 163
                    int(raw_data[i * 4 + 203]) / 128 + 0.738,    # dy, offset: 203
                    int(raw_data[i * 4 + 243]) / 128 + 0.7359,   # dz, offset: 243
                    int(raw_data[i * 4 + 283]) / 128,   # prob, offset: 283
                    int(raw_data[i * 4 + 323]) / 256,   # vx, offset: 323
                    int(raw_data[i * 4 + 363]) / 256))  # vy, offset: 363
            self.rad_d_objects.append(    # radar D, right rear
                RawObject(                 
                    int(raw_data[i * 4 + 84]) / 2048,   # ax, offset: 84
                    int(raw_data[i * 4 + 124]) / 2048,  # ay, offset: 124
                    int(raw_data[i * 4 + 164]) / 128  -0.7664,   # dx, offset: 164
                    int(raw_data[i * 4 + 204]) / 128  -0.738,    # dy, offset: 204
                    int(raw_data[i * 4 + 244]) / 128 + 0.7359,   # dz, offset: 244
                    int(raw_data[i * 4 + 284]) / 128,   # prob, offset: 284
                    int(raw_data[i * 4 + 324]) / 256,   # vx, offset: 324
                    int(raw_data[i * 4 + 364]) / 256))  # vy, offset: 364


class SensorData:
    def __init__(self, sensor_data_path):
        self.data = load_csv(sensor_data_path)[1:] # remove header
        self.timestamps = self.get_timestamps()

    def get_timestamps(self):
        times = []
        for row in self.data:
            times.append(float(row[0]))
        return times

    def get_array_at(self, time):
        for i, timestamp in enumerate(self.timestamps):
            if timestamp == time or timestamp > time:
                # organize the data
                working_data = self.data[i]
                pool = ObjectArray(working_data)
                return pool

        return None

class HostReferenceData:
    def __init__(self, reference_data_path):
        self.data = load_csv(reference_data_path)[1:] # remove header
        self.timestamps = self.get_timestamps()
        self.yaw_rates = self.get_yaw_rates()

    def get_timestamps(self):
        times = []
        for row in self.data:
            times.append(float(row[0]))
        return times

    def get_yaw_rates(self):
        yaw_rates = []
        for row in self.data:
            yaw_rates.append(float(row[3]))
        return yaw_rates

    def get_array_at(self, time):
        for i, timestamp in enumerate(self.timestamps):
            if timestamp == time or timestamp > time:
                # organize the data
                working_data = self.data[i]
                values = ReferenceValues(working_data)
                return values
        return None


def datasets_main():
    print("Loading dataset...")
    sensor_data = SensorData(r"C:\Users\Hi~\Downloads\SW Challenge 2022 - dataset\PSA_ADAS_W3_FC_2022-09-01_15-17_0060.MF4\Group_349.csv")
    print("Done loading dataset.")


    # get the data at the first timestamp
    data = sensor_data.get_array_at()
    print(data.cam_objects[0].dx)
    

if __name__ == "__main__":
    datasets_main()