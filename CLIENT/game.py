import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math, time
from config import *
from utils import distance, lerp, spawn, colliding, bullet_colliding
from network import NetworkManager
import render


def update_remote_players(network_manager, t=0.07):
    with network_manager.lock:
        for pdata in network_manager.remote_players.values():
            if "target_pos" in pdata:
                for i in range(3):
                    pdata["pos"][i] = lerp(pdata["pos"][i], pdata["target_pos"][i], t)

def main():
    pygame.init()
    display = (1920,1080)
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    hud_font = pygame.font.SysFont("Arial", 18)
    
    glEnable(GL_DEPTH_TEST)
    glClearDepth(1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(110, display[0] / display[1], 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    building_blocks = []
    center_of_wall = HOUSE_ROOF_SIZE // 2
    entrance_positions = []
    for x in range(HOUSE_ENTRANCE_WIDTH):
        for y in range(HOUSE_ENTRANCE_HEIGHT):
            pos = (x + center_of_wall - HOUSE_ENTRANCE_WIDTH // 2, y + 1, 0)
            entrance_positions.append(pos)

    for x in range(HOUSE_ROOF_SIZE):
        for z in range(HOUSE_ROOF_SIZE):
            pos = (x, HOUSE_WALL_HEIGHT + 1, z)
            building_blocks.append(pos)

    for y_level in range(0,HOUSE_WALL_HEIGHT+1):
        for x in range(HOUSE_ROOF_SIZE):
            for z in range(HOUSE_ROOF_SIZE):
                if x == 0 or z == HOUSE_ROOF_SIZE - 1 or x == HOUSE_ROOF_SIZE - 1 or z == 0:
                    pos = (x, y_level + 1, z)
                    if pos not in entrance_positions:
                        building_blocks.append(pos)


    for y in range(1, HOUSE_WALL_HEIGHT + 1):
        for z in range(HOUSE_ROOF_SIZE):

            if z != HOUSE_ROOF_SIZE // 2 or y > HOUSE_ENTRANCE_HEIGHT:
                pos = (HOUSE_ROOF_SIZE // 2, y, z)
                building_blocks.append(pos)

    #塔
    entrance_positions = []
    center_of_wall = TOWER_ROOF_SIZE//2
    for x in range(TOWER_ENTRANCE_WIDTH):
        for y in range(TOWER_ENTRANCE_HEIGHT):
            pos = (x+center_of_wall - TOWER_ENTRANCE_WIDTH//2+25,y+1,25)
            entrance_positions.append(pos)


    for x in range(TOWER_ROOF_SIZE):
        for z in range(TOWER_ROOF_SIZE):
            for y in range(TOWER_WALL_HEIGHT):
                if x == 0 or x == TOWER_ROOF_SIZE -1 or z == 0 or z == TOWER_ROOF_SIZE -1:
                    pos = (x+25,y,z+25)
                    if pos not in entrance_positions:
                        building_blocks.append(pos)

    #螺旋階段
    direction = 1 #0:左 1:上 2:右 3:下
    last_pos = [TOWER_ROOF_SIZE-2+25,-1,25]#x y z
    building = True

    exit_pos = []

    while building:
        if last_pos[1] == TOWER_WALL_HEIGHT-2:
            building = False
            break

        last_pos[1] +=1
        if direction == 0:
            pos = last_pos
            pos[0]+=1
            if not pos[0] == 25+TOWER_ROOF_SIZE-1:
                last_pos = pos
                pos = tuple(pos)
                building_blocks.append(pos)
            else:

                pos[0]-=1
                direction =1
                last_pos[1]-=1

        elif direction == 1:
            pos = last_pos
            pos[2]+=1
            if not pos[2] == 25+TOWER_ROOF_SIZE-1:
                last_pos = pos
                pos = tuple(pos)
                building_blocks.append(pos)
            else:
                direction =2
                pos[2]-=1
                last_pos[1]-=1

        elif direction == 2:

            pos = last_pos
            pos[0]-=1
            if not pos[0] == 25:
 
                last_pos = pos
                pos=tuple(pos)
            
                building_blocks.append(pos)
            else:
                pos[0]+=1
                direction =3
                last_pos[1]-=1

        elif direction == 3:
            pos = last_pos
            pos[2]-=1
            if not pos[2] == 25:
                last_pos = pos
                pos = tuple(pos)
                building_blocks.append(pos)
            else:
                pos[2]+=1
                direction =0
                last_pos[1]-=1

    exit_pos = []
    if direction == 0:
        for i in range(-8, 1):
            exit_pos.append((last_pos[0] + i, last_pos[1], last_pos[2]))
    elif direction == 1:
        for i in range(-8, 1):
            exit_pos.append((last_pos[0], last_pos[1], last_pos[2] + i))
    elif direction == 2:
        for i in range(-1, 8):
            exit_pos.append((last_pos[0] + i, last_pos[1], last_pos[2]))
    elif direction == 3:
        for i in range(-1, 8):
            exit_pos.append((last_pos[0], last_pos[1], last_pos[2] + i))

    for x in range(TOWER_ROOF_SIZE):
        for z in range(TOWER_ROOF_SIZE):
            pos = (x+25,TOWER_WALL_HEIGHT-2,z+25)
            if pos not in exit_pos:
                building_blocks.append(pos)

    merged_blocks_dl = render.create_merged_blocks_display_list(building_blocks)

    clock = pygame.time.Clock()

    camera_pos = spawn(building_blocks)
    camera_yaw = 0.0
    camera_pitch = 0.0
    y_velocity = 0.0
    on_ground = True

    network_manager = NetworkManager()

    network_manager.start_receiving()

    last_shot_time = time.time()
    last_state_send_time = time.time()

    local_bullets = []

    running = True
    while running:

        for event in pygame.event.get():

            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False

        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        camera_yaw += mouse_dx * MOUSE_SENSITIVITY
        camera_pitch -= mouse_dy * MOUSE_SENSITIVITY
        camera_pitch = max(-89, min(89, camera_pitch))

        keys = pygame.key.get_pressed()
        dx = dz = 0
        yaw_rad = math.radians(camera_yaw)
        if keys[pygame.K_w]:
            dx += math.sin(yaw_rad) * MOVE_SPEED
            dz -= math.cos(yaw_rad) * MOVE_SPEED
        if keys[pygame.K_s]:
            dx -= math.sin(yaw_rad) * MOVE_SPEED
            dz += math.cos(yaw_rad) * MOVE_SPEED
        if keys[pygame.K_a]:
            dx -= math.cos(yaw_rad) * MOVE_SPEED
            dz -= math.sin(yaw_rad) * MOVE_SPEED
        if keys[pygame.K_d]:
            dx += math.cos(yaw_rad) * MOVE_SPEED
            dz += math.sin(yaw_rad) * MOVE_SPEED


        if keys[pygame.K_SPACE] and on_ground:
            y_velocity = JUMP_STRENGTH
            on_ground = False


        
        y_velocity += GRAVITY
        if not colliding(camera_pos[0], camera_pos[1] + y_velocity, camera_pos[2], building_blocks) and (camera_pos[1] + y_velocity) >= 1:
            camera_pos[1] += y_velocity
            on_ground = False
        else:
            y_velocity = 0
            on_ground= True

        if camera_pos[1] <= 2.5:
            camera_pos[1] = 2.5
            on_ground = True

        if camera_pos[1] >= 120:
            camera_pos[1] = 120

        current_time = time.time()

        if pygame.mouse.get_pressed()[0] and (current_time - last_shot_time >= FIRE_RATE):
            pitch_rad = math.radians(camera_pitch)
            cos_pitch = math.cos(pitch_rad)
            sin_pitch = math.sin(pitch_rad)
            camDir_x = cos_pitch * math.sin(yaw_rad)
            camDir_y = sin_pitch
            camDir_z = -cos_pitch * math.cos(yaw_rad)
            bullet = {
                "pos": camera_pos.copy(),
                "dir": [camDir_x, camDir_y, camDir_z],
                "speed": 1,
                "spawn_time": current_time,
                "lifetime": 3.0
            }
            local_bullets.append(bullet)
            bullet_msg = {
                "id": network_manager.client_id,
                "type": "bullet",
                "pos": bullet["pos"],
                "dir": bullet["dir"]
            }
            network_manager.send(bullet_msg)
            last_shot_time = current_time

        new_x = camera_pos[0] + dx
        if not colliding(new_x, camera_pos[1], camera_pos[2], building_blocks):
            camera_pos[0] = new_x
        new_z = camera_pos[2] + dz
        if not colliding(camera_pos[0], camera_pos[1], new_z, building_blocks):
            camera_pos[2] = new_z

        if current_time - last_state_send_time > UPDATE_INTERVAL:
            state_msg = {
                "id": network_manager.client_id,
                "pos": [camera_pos[0],camera_pos[1]-2,camera_pos[2]],
                "yaw": camera_yaw,
                "pitch": camera_pitch,
                "type": "state"
            }
            network_manager.send(state_msg)
            last_state_send_time = current_time

        update_remote_players(network_manager)

        for bullet in local_bullets[:]:
            bullet_pre_pos = [bullet["pos"][i] + bullet["dir"][i] * bullet["speed"] for i in range(3)]
            if current_time - bullet["spawn_time"] > bullet["lifetime"]:
                local_bullets.remove(bullet)
                continue
            hit_detected = False
            with network_manager.lock:
                for pid, pdata in network_manager.remote_players.items():
                    if distance(bullet["pos"], [pdata["pos"][0], pdata["pos"][1] + 2, pdata["pos"][2]]) < 1.2:
                        hit_msg = {
                            "id": network_manager.client_id,
                            "type": "hit",
                            "target": pid,
                            "damage": 20,
                            "shooter": network_manager.client_id
                        }
                        network_manager.send(hit_msg)
                        hit_detected = True
                        break
            if hit_detected:
                local_bullets.remove(bullet)
            if bullet in local_bullets:
                if bullet_colliding(bullet_pre_pos[0], bullet_pre_pos[1], bullet_pre_pos[2], building_blocks):
                    local_bullets.remove(bullet)
                    continue
                bullet["pos"] = bullet_pre_pos

        with network_manager.lock:
            for bullet in network_manager.remote_bullets[:]:
                bullet_pre_pos = [bullet["pos"][i] + bullet["dir"][i] * bullet["speed"] for i in range(3)]
                if colliding(bullet_pre_pos[0], bullet_pre_pos[1], bullet_pre_pos[2], building_blocks):
                    network_manager.remote_bullets.remove(bullet)
                    continue
                bullet["pos"] = bullet_pre_pos
                if current_time - bullet["spawn_time"] > bullet["lifetime"]:
                    network_manager.remote_bullets.remove(bullet)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        pitch_rad = math.radians(camera_pitch)
        cos_pitch = math.cos(pitch_rad)
        sin_pitch = math.sin(pitch_rad)
        camDir_x = cos_pitch * math.sin(yaw_rad)
        camDir_y = sin_pitch
        camDir_z = -cos_pitch * math.cos(yaw_rad)
        gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
                  camera_pos[0] + camDir_x, camera_pos[1] + camDir_y, camera_pos[2] + camDir_z,
                  0, 1, 0)

        glBegin(GL_QUADS)
        glColor3f(0.3, 0.3, 0.3)
        glVertex3f(-50, 0, -50)
        glVertex3f(-50, 0, 50)
        glVertex3f(50, 0, 50)
        glVertex3f(50, 0, -50)
        glEnd()

        glCallList(merged_blocks_dl)

        glPointSize(5)
        glBegin(GL_POINTS)
        glColor3f(1.0, 0.0, 0.0)
        for bullet in local_bullets:
            glVertex3f(bullet["pos"][0], bullet["pos"][1], bullet["pos"][2])
        glColor3f(0.0, 0.0, 1.0)
        with network_manager.lock:
            for bullet in network_manager.remote_bullets:
                glVertex3f(bullet["pos"][0], bullet["pos"][1], bullet["pos"][2])
        glEnd()

        with network_manager.lock:
            for pdata in network_manager.remote_players.values():
                render.draw_human_figure(pdata["pos"], pdata["yaw"])

        if network_manager.player_hp <= 0:
            camera_pos = spawn(building_blocks)
            network_manager.player_hp = PLAYER_MAX_HP
            on_ground = False
        
        render.draw_hud(display, hud_font, network_manager.player_hp)




        pygame.display.flip()
        clock.tick(120)

    network_manager.stop()
    pygame.quit()
