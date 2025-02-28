from OpenGL.GL import *

from OpenGL.GLU import *
import pygame
import math

cube_vertices = (
    ( 1, -1, -1),
    ( 1,  1, -1),
    (-1,  1, -1),
    (-1, -1, -1),
    ( 1, -1,  1),
    ( 1,  1,  1),
    (-1, -1,  1),
    (-1,  1,  1)
)
cube_surfaces = (
    (0,1,2,3),
    (3,2,7,6),
    (6,7,5,4),
    (4,5,1,0),
    (1,5,7,2),
    (4,0,3,6)
)

def create_cube_display_list(color=(0.8, 0.5, 0.2)):
    dl = glGenLists(1)
    glNewList(dl, GL_COMPILE)
    glBegin(GL_QUADS)
    glColor3fv(color)
    for surface in cube_surfaces:
        for vertex in surface:
            glVertex3fv(cube_vertices[vertex])
    glEnd()
    glColor3f(0.0, 0.0, 0.0)
    glBegin(GL_LINES)
    for surface in cube_surfaces:
        for i in range(len(surface)):
            glVertex3fv(cube_vertices[surface[i]])
            glVertex3fv(cube_vertices[surface[(i+1)%len(surface)]])
    glEnd()
    glEndList()
    return dl

def draw_cube_at(position, display_list, size=1.0):
    glPushMatrix()
    glTranslatef(position[0], position[1], position[2])
    glScalef(size/2.0, size/2.0, size/2.0)
    glCallList(display_list)
    glPopMatrix()
    
def draw_human_figure(position, yaw, color=(0.0, 1.0, 0.0)):
    glPushMatrix()
    glTranslatef(position[0], position[1], position[2])
    glRotatef(yaw, 0, 1, 0)
    glColor3fv(color)

    glPushMatrix()
    glTranslatef(0, 1.8, 0)
    glBegin(GL_LINE_LOOP)
    for i in range(36):
        angle = 2 * math.pi * i / 36
        glVertex3f(0.2 * math.cos(angle), 0.2 * math.sin(angle), 0)
    glEnd()
    glPopMatrix()

    glBegin(GL_LINES)
    glVertex3f(0, 1.75, 0)
    glVertex3f(0, 1.65, 0)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(0, 1.65, 0)
    glVertex3f(0, 1.0, 0)
    glEnd()

    glBegin(GL_LINES)

    glVertex3f(0, 1.55, 0)
    glVertex3f(-0.5, 1.3, 0)

    glVertex3f(0, 1.55, 0)
    glVertex3f(0.5, 1.3, 0)
    glEnd()

    glBegin(GL_LINES)

    glVertex3f(0, 1.0, 0)
    glVertex3f(-0.3, 0.0, 0)

    glVertex3f(0, 1.0, 0)
    glVertex3f(0.3, 0.0, 0)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(0, 1.3, 0)
    glVertex3f(0, 1.3, 0.6)
    glEnd()
    glBegin(GL_LINES)
    glVertex3f(0, 1.3, 0.6)
    glVertex3f(0.1, 1.3, 0.5)
    glVertex3f(0, 1.3, 0.6)
    glVertex3f(-0.1, 1.3, 0.5)
    glEnd()
    
    glPopMatrix()
def draw_fov_indicator(camera_pos, camera_yaw):
    glPushMatrix() 
    glColor3f(1.0, 1.0, 0.0) 

    try:
        glBegin(GL_LINE_STRIP) 
        for angle in range(-10, 11, 2): 
            rad = math.radians(camera_yaw + angle)
            x = camera_pos[0] + math.sin(rad) * 5
            z = camera_pos[2] - math.cos(rad) * 5
            glVertex3f(x, camera_pos[1], z)
        glEnd()
    except OpenGL.error.GLError as e:
        print(f"OpenGL Error in draw_fov_indicator: {e}")

    glPopMatrix()

def draw_text(x, y, text, font, color=(255,255,255)):
    text_surface = font.render(text, True, color)
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def draw_hud(display_size, hud_font, player_hp):
    width, height = display_size
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

    glColor3f(1,1,1)
    glBegin(GL_LINES)
    cx, cy = width // 2, height // 2
    glVertex2f(cx - 10, cy)
    glVertex2f(cx + 10, cy)
    glVertex2f(cx, cy - 10)
    glVertex2f(cx, cy + 10)
    glEnd()

    bar_x = 20
    bar_y = 20
    bar_width = 100
    bar_height = 20

    glColor3f(0.5, 0, 0)
    glBegin(GL_QUADS)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + bar_width, bar_y)
    glVertex2f(bar_x + bar_width, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()

    glColor3f(0, 1, 0)
    current_width = (player_hp / 100.0) * bar_width
    glBegin(GL_QUADS)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + current_width, bar_y)
    glVertex2f(bar_x + current_width, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()

    draw_text(bar_x, bar_y + bar_height + 5, f"HP: {player_hp}", hud_font)

    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
