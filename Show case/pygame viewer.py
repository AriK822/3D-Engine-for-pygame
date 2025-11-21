from Arik_3d_engin import *
import pygame
import sys
from math import sqrt, sin, cos, pi
from random import randint
from time import time



pygame.init()
clock = pygame.time.Clock()
WIDTH, HEIGHT = 700, 700
PADDING = 50

WHITE = (255, 255, 255)
BLACK = (25, 25, 25)
GRAY = (100, 100, 100)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D rendered game")
screen.fill(BLACK)

Font=pygame.font.SysFont('timesnewroman',  25)

gun = pygame.image.load('assets/gun.png').convert_alpha()
gun_rect = gun.get_rect(center = (WIDTH - 70, HEIGHT - 120))

shot_fire = pygame.image.load('assets/shot_fire.png').convert_alpha()
shot_fire = pygame.transform.scale(shot_fire, (100, 100))
shot_fire = pygame.transform.rotate(shot_fire, 45)
shot_fire.set_alpha(0)
shot_fire_rect = shot_fire.get_rect(center = (WIDTH - 230, HEIGHT - 210))

gun_sfx = pygame.mixer.Sound("assets/gunshot_sfx.wav")


class PygameHandler(object):
    def __init__(self, world: World):
        self.world = world
        self._visible_mouse = True
        self._full_screen = False
        self.bullet_animation_p = 1
        self.gun_animation_p = 1
        self.crouch_animation_p = pi / 2
        self.gun_rect = gun_rect
        self.screen_middle = (WIDTH // 2, HEIGHT // 2)
        self.shot_fire_trasparancy = 0
        self.hits = 0


    def bullet_animation(self):
        if self.bullet_animation_p < 1:
            stat_pos = (WIDTH, HEIGHT)
            end_pos = (WIDTH // 2, HEIGHT // 2)
            return (stat_pos[0] - end_pos[0] * self.bullet_animation_p, stat_pos[1] - end_pos[1] * self.bullet_animation_p)

        else:
            self.bullet_animation_p = 1
            return False
        

    def gun_animation(self):
        if self.gun_animation_p < 1:
            stat_pos = (WIDTH - 30, HEIGHT - 90)
            end_pos = (WIDTH - 70, HEIGHT - 120)
            rect_pos = (stat_pos[0] - (stat_pos[0] - end_pos[0]) * self.gun_animation_p,
                        stat_pos[1] - (stat_pos[1] - end_pos[1]) * self.gun_animation_p)
            self.gun_rect = gun.get_rect(center = rect_pos)

        else:
            self.gun_animation_p = 1


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

        if draw_bullet:
            self.bullet_animation_p += 0.15 / world.fps * 75
            bp = self.bullet_animation()
            if bp:
                pygame.draw.line(screen, WHITE, (bp[0] - 10, bp[1] - 10), bp, 4)

        if draw_shot_fire:
            self.shot_fire_trasparancy -= 50 / world.fps * 75
            self.shot_fire_trasparancy = 0 if self.shot_fire_trasparancy < 0 else self.shot_fire_trasparancy
            shot_fire.set_alpha(self.shot_fire_trasparancy)
            screen.blit(shot_fire, shot_fire_rect)

        if draw_gun:
            self.gun_animation_p += 0.05 / world.fps * 75
            self.gun_animation()
            screen.blit(gun, self.gun_rect)

        if draw_hits:
            hit_counter = Font.render(f"Score: {self.hits}", False, WHITE, None)
            screen.blit(hit_counter, hit_counter.get_rect(center=(60, 30)))

        if draw_fps:
            hit_counter = Font.render(f"FPS: {world.render_fps()}", False, WHITE, None)
            screen.blit(hit_counter, hit_counter.get_rect(center=(WIDTH - 60, 30)))

        if draw_cross_hair:
            cross_hair_size = (WIDTH + HEIGHT) // 100
            pygame.draw.line(screen, WHITE, (WIDTH // 2 - cross_hair_size, HEIGHT // 2), (WIDTH // 2 + cross_hair_size, HEIGHT // 2), 2)
            pygame.draw.line(screen, WHITE, (WIDTH // 2, HEIGHT // 2 - cross_hair_size), (WIDTH // 2, HEIGHT // 2 + cross_hair_size), 2)

        pygame.display.flip()


    def bullet_collision(self):
        for i, polygon in enumerate(world.rendered_f_e[::-1]):
            i = len(world.rendered_f_e) - 1 - i
            if world.f_e_look_up[i] == 'f' and not world.obj_look_up_f_e[i].hit and not world.obj_look_up_f_e[i].is_shadow:
                if world.ray_trace_collion_detector((0, 0), polygon):
                        world.obj_look_up_f_e[i].hit = True
                        self.hits += 1
                        break


    def process_gunshot(self):
        gun_sfx.play()
        self.bullet_animation_p = 0.2
        self.gun_animation_p = 0
        self.shot_fire_trasparancy = 255
        self.bullet_collision()
        self.process_hit()


    def process_hit(self):
        for obj in world.objects:
            if obj.hit:
                if obj.shadows_on:
                    world.objects.remove(obj.shadow_obj)
                world.objects.remove(obj)

                new_cube = Cube([randint(-50, 50), randint(10, 100), randint(-50, 50)], randint(10, 30))
                world.objects.append(new_cube)
                world.objects.append(new_cube.shadow())







world = World()
world.shading = True

# cube1 = Cube([0, 0, 40])
sniper = world.load_obj('assets/Sniper_Rifle.obj', 3, center=[-20, 17, 50], edge_colors=[], face_colors=[], show_edge=False)
wolf = world.load_obj('assets/Wolf_obj.obj', 20, center=[0, 20, 60])
man = world.load_obj('assets/Man.obj', 5, center=[20, 14, 30], show_edge=False, face_colors=(230, 210, 190))
# kunai = world.load_obj('assets/Kunai.obj', 20, center=[20, 14, 30], show_edge=False, face_colors=(230, 210, 190))

world.objects += [man, sniper, wolf]
# world.objects += [kunai]
# world.objects += [cube1]


world.render()

handler = PygameHandler(world)
handler.draw()

print(world)

running = True
holding_mouse = False
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
                handler.process_gunshot()
                last_shot = time()
                holding_mouse = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                holding_mouse = False

        elif event.type == pygame.MOUSEMOTION:
            dx, dy = event.rel
            if not handler.visible_mouse:
                world.horizantle_angle += dx * world.sensitivity
                world.vertical_angle += dy * world.sensitivity

        elif holding_mouse and event.type == pygame.MOUSEMOTION:
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
                world.jump()


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

    if holding_mouse:
        if time() - last_shot > .2:
            handler.process_gunshot()
            last_shot = time()

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


    for obj in world.objects:
        obj.h_angle += 1 / world.fps * 25


    world.render()
    handler.draw(draw_vertecies = False, draw_edges = True, draw_faces = True, draw_gun = True, draw_bullet = True, 
             draw_cross_hair = True, draw_shot_fire = True, draw_hits = True, draw_fps = True)

    clock.tick(75)



pygame.quit()
sys.exit()



