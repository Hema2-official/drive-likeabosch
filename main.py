import enum
import pygame
from datasets import *
from draw_utils import *
from common_types import *
import time

pygame.init()

sensor_data = SensorData(r"C:\Users\Hi~\Downloads\SW Challenge 2022 - dataset\PSA_ADAS_W3_FC_2022-09-01_15-12_0059.MF4\Group_349.csv")
host_reference = HostReferenceData(r"C:\Users\Hi~\Downloads\SW Challenge 2022 - dataset\PSA_ADAS_W3_FC_2022-09-01_15-12_0059.MF4\Group_416.csv")

# main loop
running = True
timestamp_index = 0
Timestamp_offset = sensor_data.timestamps[0]
starting_time = time.time()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill screen with white
    clear_screen()

    # draw blindzones
    draw_rect((-0.3,0.8), (-0.3,2.3), (2, 2.3), (2, 0.8), (255, 0, 0))
    draw_rect((-0.3,-0.8), (-0.3,-2.3), (2, -2.3), (2, -0.8), (255, 0, 0))

    # wait until the next timestamp
    while time.time() - starting_time < sensor_data.timestamps[timestamp_index] - Timestamp_offset:
        pass

    draw_image(imgs[ObjType.truck], (0, 0))
    
    obj_array = sensor_data.get_array_at(sensor_data.timestamps[timestamp_index])
    ref = host_reference.get_array_at(sensor_data.timestamps[timestamp_index])

    for obj in obj_array.cam_objects:
        draw_object(obj, ref)

    for obj in obj_array.rad_a_objects:
        draw_object(obj, ref)
        
    for obj in obj_array.rad_b_objects:
        draw_object(obj, ref)

    for obj in obj_array.rad_c_objects:
        draw_object(obj, ref)
        
    for obj in obj_array.rad_d_objects:
        draw_object(obj, ref)
        
    print(sensor_data.timestamps[timestamp_index])
    timestamp_index += 1

    # flip screen
    pygame.display.flip()

#quit pygame
pygame.quit()

