import pygame
from datasets import *
from draw_utils import *
from common_types import *
from environment import *
import time

pygame.init()

pack = "datasets/PSA_ADAS_W3_FC_2022-09-01_14-49_0054.MF4"
sensor_data = SensorData(pack + "/Group_349.csv")
host_reference = HostReferenceData(pack + "/Group_416.csv")

# main loop
running = True

timestamp_index = 1
timestamp_offset = sensor_data.timestamps[0]
starting_time = time.time()

background = Background("assets/images/background.jpg")
lane_lines = LaneLines()

environment = Environment()
visuals_mode = 1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                timestamp_index += 1000
                timestamp_offset = sensor_data.timestamps[timestamp_index]
                starting_time = time.time()
            if event.key == pygame.K_LEFT:
                timestamp_index -= 1000
                timestamp_offset = sensor_data.timestamps[timestamp_index]
                starting_time = time.time()
            if event.key == pygame.K_0:
                visuals_mode = 0
            if event.key == pygame.K_1:
                visuals_mode = 1
            if event.key == pygame.K_2:
                visuals_mode = 2


    # fill screen with white
    clear_screen()

    # wait until the next timestamp
    while time.time() - starting_time < sensor_data.timestamps[timestamp_index] - timestamp_offset:
        pass

    # prepare the data for visualization
    obj_array = sensor_data.get_array_at(sensor_data.timestamps[timestamp_index])
    ref = host_reference.get_array_at(sensor_data.timestamps[timestamp_index])

    # draw background
    background.update(ref.vx, sensor_data.timestamps[timestamp_index] - sensor_data.timestamps[timestamp_index - 1])
    background.draw()

    # draw lane lines around the car based on the yaw angle
    lane_lines.update(ref.yaw)
    lane_lines.draw()                         # look guys i forgot to implement this but it doesn't affect anything

    # draw a steering wheel rotated by the yaw rate
    draw_image(img_yoke, (screen_size[0] / 4, screen_size[1] / 5 * 4), (80, 50), math.degrees(ref.yaw), abs_pos=True)

    # draw car
    draw_image(imgs[2], (0, 0), (8, 17))

    # draw blindzones
    draw_rect((-0.3,0.8), (-0.3,2.3), (2, 2.3), (2, 0.8), (255, 0, 0))
    draw_rect((-0.3,-0.8), (-0.3,-2.3), (2, -2.3), (2, -0.8), (255, 0, 0))

    # print out details
    draw_text("Time (s): " + str(round(sensor_data.timestamps[timestamp_index], 3)), (0, 0))
    draw_text("Speed (m/s): " + str(ref.vx), (0, 20))
    draw_text("Speed (km/h): " + str(round(ref.vx * 3.6, 3)), (0, 40))
    draw_text("Acceleration (m/s^2): " + str(ref.ax), (0, 60))
    draw_text("Yaw rate: " + str(ref.yaw), (0, 80))
    draw_text("Press 0/1/2 to switch between visualizations", (0, 100))

    # VISUALIZATION MODE 1 (PART 1): draw the simulation
    if visuals_mode == 1:
        for obj in environment.objects:
            draw_circle((obj.dx, obj.dy), (0, 0, 255), 2)
            
    # update the environment
    environment.update(obj_array, ref, sensor_data.timestamps[timestamp_index] - sensor_data.timestamps[timestamp_index - 1])

    # Check environment safety
    warnings = environment.check_safety()
    for warning in warnings:
        warn_timeouts[warning] = 4
    draw_warnings(sensor_data.timestamps[timestamp_index] - sensor_data.timestamps[timestamp_index - 1])
    

    # VISUALIZATION MODE 0: draw all of the sensor data
    if visuals_mode == 0:
        # draw the objects
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

    # VISUALIZATION MODE 1 (PART 2): draw the simulation
    if visuals_mode == 1:
        for obj in environment.temporary_objects:
            draw_circle((obj.dx, obj.dy), (255, 0, 0), 2)
        for obj in environment.objects:
            draw_circle((obj.dx, obj.dy), (0, 255, 0), 1.6)

    # VISUALIZATION MODE 2: draw the objects in the environment
    if visuals_mode == 2:
        for obj in environment.objects:
            draw_object(obj, ref)

    
    # increment the timestamp
    if timestamp_index < len(sensor_data.timestamps) - 1:
        timestamp_index += 1
    else:
        running = False

    # swap frame buffers
    pygame.display.flip()

#quit pygame
pygame.quit()

