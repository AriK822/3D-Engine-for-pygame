from Arik_3d_engin import *
import pygame
import sys
from math import sqrt
from random import randint
from time import time



pygame.init()
clock = pygame.time.Clock()
WIDTH, HEIGHT = 700, 700
PADDING = 50

WHITE = (255, 255, 255)
BLACK = (25, 25, 25)
GRAY = (200, 200, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D rendered game")
screen.fill(BLACK)

Font=pygame.font.SysFont('timesnewroman',  25)

gun = pygame.image.load('assets/hand.png').convert_alpha()
gun_rect = gun.get_rect(center = (WIDTH - 70, HEIGHT - 100))

break_sfx = pygame.mixer.Sound("assets/Dirt.mp3")
place_sfx = pygame.mixer.Sound("assets/Dirt.mp3")


class PygameHandler(object):
    def __init__(self, world):
        self.world = world
        self._visible_mouse = True
        self._full_screen = False
        self.hand_animation_p = 1
        self.gun_rect = gun_rect
        self.screen_middle = (WIDTH // 2, HEIGHT // 2)
        self.filled_grid = [world.objects[0].center]
        self.ground = -5
        

    def hand_animation(self):
        if self.hand_animation_p < 1:
            stat_pos = (WIDTH - 70, HEIGHT - 100)
            end_pos = (WIDTH - 50, HEIGHT - 70)
            rect_pos = (stat_pos[0] - (stat_pos[0] - end_pos[0]) * self.hand_animation_p,
                        stat_pos[1] - (stat_pos[1] - end_pos[1]) * self.hand_animation_p)
            self.gun_rect = gun.get_rect(center = rect_pos)

        else:
            self.hand_animation_p = 1


    @property
    def visible_mouse(self):
        return self._visible_mouse
    

    @visible_mouse.setter
    def visible_mouse(self, value):
        self._visible_mouse = value

        if value:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
        else:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)


    @property
    def full_screen(self):
        return self._full_screen
    

    @full_screen.setter
    def full_screen(self, value):
        self._full_screen = value

        if value:
            pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
        else:
            pygame.display.set_mode((WIDTH, HEIGHT))


    def draw(self, draw_vertecies = True, draw_edges = True, draw_faces = True, draw_gun = True, draw_bullet = True, 
             draw_cross_hair = True, draw_shot_fire = True, draw_hits = True, draw_fps = True):
        screen.fill(BLACK)

        if draw_vertecies:
            for vertex in self.world.rendered_vertecies:
                equavalent_coords = (WIDTH / 2 + (vertex[0] * WIDTH / self.world.fov), HEIGHT / 2 - (vertex[1] * HEIGHT / self.world.fov))
                pygame.draw.circle(screen, WHITE, equavalent_coords, 5)
        
        # Draw faces & vertecies
        for i, f_e in enumerate(self.world.rendered_f_e):
            f_e_vertecies = []
            for vertex in f_e:
                equavalent_coords = (WIDTH / 2 + (vertex[0] * WIDTH / self.world.fov), HEIGHT / 2 - (vertex[1] * HEIGHT / self.world.fov))
                f_e_vertecies.append(equavalent_coords)

            if world.f_e_look_up[i] == 'f':
                if draw_faces:
                    pygame.draw.polygon(screen, world.rendered_f_e_colors[i], f_e_vertecies)
            elif world.f_e_look_up[i] == 'e':
                if draw_edges:
                    pygame.draw.polygon(screen, world.rendered_f_e_colors[i], f_e_vertecies, 3)


        if draw_gun:
            self.hand_animation_p += 0.05 / world.fps * 75
            self.hand_animation()
            screen.blit(gun, self.gun_rect)


        if draw_fps:
            hit_counter = Font.render(f"FPS: {world.render_fps()}", False, WHITE, None)
            screen.blit(hit_counter, hit_counter.get_rect(center=(WIDTH - 60, 30)))

        if draw_cross_hair:
            cross_hair_size = (WIDTH + HEIGHT) // 100
            pygame.draw.line(screen, WHITE, (WIDTH // 2 - cross_hair_size, HEIGHT // 2), (WIDTH // 2 + cross_hair_size, HEIGHT // 2), 2)
            pygame.draw.line(screen, WHITE, (WIDTH // 2, HEIGHT // 2 - cross_hair_size), (WIDTH // 2, HEIGHT // 2 + cross_hair_size), 2)

        pygame.display.flip()


    def break_block(self):
        self.hand_animation_p = 0
        for i, polygon in enumerate(world.rendered_f_e[::-1]):
            i = len(world.rendered_f_e) - 1 - i
            if world.f_e_look_up[i] == 'f' and not world.obj_look_up_f_e[i].is_shadow:
                if world.ray_trace_collion_detector((0, 0), polygon):
                    break_sfx.play()
                    self.filled_grid.remove(world.obj_look_up_f_e[i].center)
                    world.objects.remove(world.obj_look_up_f_e[i])
                    break


    def place_block(self):
        self.hand_animation_p = 0
        for i, polygon in enumerate(world.rendered_f_e[::-1]):
            i = len(world.rendered_f_e) - 1 - i
            if world.f_e_look_up[i] == 'f':
                if world.ray_trace_collion_detector((0, 0), polygon):
                    place_sfx.play()
                    grid = world.obj_look_up_f_e[i].center
                    direction = world.rendered_face_directions[i]
                    new_grid = grid.copy()
                    
                    match direction:
                        case 'x+':
                            new_grid[0] += 10
                        case 'x-':
                            new_grid[0] -= 10
                        case 'z+':
                            new_grid[2] += 10
                        case 'z-':
                            new_grid[2] -= 10
                        case 'y+':
                            new_grid[1] += 10
                        case 'y-':
                            new_grid[1] -= 10

                    if new_grid in self.filled_grid:
                        break

                    new_cube = Cube(center=new_grid, block_type='grass', edge_colors=GRAY)
                    world.objects += [new_cube]
                    self.filled_grid.append(new_grid)
                    break


    def handle_block_climb(self):
        shifts = []
        px, py, pz = world.shift
        for x, y, z in self.filled_grid:
            if x - 5 <= -px <= x + 5 and z - 5 <= -pz <= z + 5:
                shifts.append(-y - 25)
        
        self.shifts = shifts

        if shifts:
            world.shift[1] = min(shifts)
        else:
            world.shift[1] = self.ground








world = World()
world.shading = False

cube1 = Cube([0, -10, 40], block_type='grass', edge_colors=GRAY)
cube1.is_shadow = True
world.objects += [cube1]

world.render()

handler = PygameHandler(world)
handler.draw()

print(world)

running = True
holding_mouse_right = False
holding_mouse_left = False
holding_w = False
holding_s = False
holding_a = False
holding_d = False
holding_shift = False


while running:
    mousex, mousey = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            handler.visible_mouse = False
            handler.full_screen = True

            if event.button == 1:
                handler.break_block()
                last_break = time()
                holding_mouse_right = True

            elif event.button == 3:
                handler.place_block()
                last_place = time()
                holding_mouse_left = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                holding_mouse_right = False
            elif event.button == 3:
                holding_mouse_left = False

        elif event.type == pygame.MOUSEMOTION:
            dx, dy = event.rel
            if not handler.visible_mouse:
                world.horizantle_angle += dx * world.sensitivity
                world.vertical_angle += dy * world.sensitivity

        elif holding_mouse_right and event.type == pygame.MOUSEMOTION:
            pass


        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                handler.visible_mouse = True
                handler.full_screen = False
            if event.key == pygame.K_F11:
                handler.full_screen = not handler.full_screen


            if event.key == pygame.K_w:
                holding_w = True
            if event.key == pygame.K_s:
                holding_s = True
            if event.key == pygame.K_a:
                holding_a = True
            if event.key == pygame.K_d:
                holding_d = True
            if event.key == pygame.K_LSHIFT:
                holding_shift = True
            if event.key == pygame.K_SPACE:
                pass


        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                holding_w = False
                world.smooth_stop_w()
            if event.key == pygame.K_s:
                holding_s = False
                world.smooth_stop_s()
            if event.key == pygame.K_a:
                holding_a = False
                world.smooth_stop_a()
            if event.key == pygame.K_d:
                holding_d = False
                world.smooth_stop_d()
            if event.key == pygame.K_LSHIFT:
                holding_shift = False

    if holding_mouse_right:
        if time() - last_break > .2:
            handler.break_block()
            last_break = time()

    if holding_mouse_left:
        if time() - last_place > .2:
            handler.place_block()
            last_place = time()

    if (holding_w ^ holding_s) and (holding_a ^ holding_d):
        world.speed_multiplier /= sqrt(2)

    if holding_shift:
        world.speed_multiplier *= 2

    if holding_w:
        world.shift_forward()
    if holding_s:
        world.shift_backward()
    if holding_a:
        world.shift_left()
    if holding_d:
        world.shift_right()

    world.speed_multiplier = 1
    world.handle_acceleration()

    handler.handle_block_climb()
    world.render()
    handler.draw(draw_vertecies=False, draw_edges=True)

    clock.tick(75)



pygame.quit()
sys.exit()



