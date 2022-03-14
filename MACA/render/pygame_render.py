
import os
import pygame
import pygame.gfxdraw
import numpy as np

from MACA.fighter.fighter_type import FIGHTER_TYPE

MAP_SCALE = 1
class PygameRender():
    def __init__(self, args, allies, enemies):
        self.args = args
        self.allies = allies
        self.enemies = enemies
        self.draw_reconn_detect_range = args.render_setting.draw_reconn_detect_range
        self.draw_fighter_detect_range = args.render_setting.draw_fighter_detect_range
        self.draw_damage_range = args.render_setting.draw_damage_range

        pygame.init()

        self.ally_cannon = pygame.transform.scale(
            pygame.image.load(args.render_setting.ally_cannon_path), 
            (args.render_setting.scale_val, args.render_setting.scale_val))
        self.ally_reconn = pygame.transform.scale(
            pygame.image.load(args.render_setting.ally_reconn_path), 
            (args.render_setting.scale_val, args.render_setting.scale_val))
        self.ally_missile = pygame.transform.scale(
            pygame.image.load(args.render_setting.ally_missile_path), 
            (args.render_setting.scale_val, args.render_setting.scale_val))
        self.enemy_cannon = pygame.transform.scale(
            pygame.image.load(args.render_setting.enemy_cannon_path), 
            (args.render_setting.scale_val, args.render_setting.scale_val))
        self.enemy_reconn = pygame.transform.scale(
            pygame.image.load(args.render_setting.enemy_reconn_path), 
            (args.render_setting.scale_val, args.render_setting.scale_val))
        self.enemy_missile = pygame.transform.scale(
            pygame.image.load(args.render_setting.enemy_missile_path), 
            (args.render_setting.scale_val, args.render_setting.scale_val))

        self.size = args.simulator.map_x_limit * MAP_SCALE, args.simulator.map_y_limit * MAP_SCALE
        self.screen = pygame.display.set_mode(self.size)

        self.screen.fill((255, 255, 255))

        self.image_name_count = 0

    def render(self, save_pic=False):
        self.screen.fill((255, 255, 255))
        surface = pygame.Surface(self.size, pygame.SRCALPHA)

        for i in range(0, 1600, 100):
            for j in range(0, 500, 100):
                color = (128, 125, 125, 32)
                if ((i + j) / 100) % 2 == 0:
                    color = (0, 238, 171, 32)
                pygame.draw.rect(surface, color, [i, j, 100, 100], 0)

        for i in range(0, 1600, 100):
            for j in range(0, 500, 100):
                pygame.draw.line(surface, (96, 96, 96, 32), (0, j), (800, j))
                pygame.draw.line(surface, (96, 96, 96, 32), (i, 0), (i, 500))
        self.screen.blit(surface, (0, 0,))


        for ally in self.allies:
            if ally.alive:
                if ally.type == FIGHTER_TYPE['reconnaissance']:
                    ally_reconn = pygame.transform.rotate(self.ally_reconn, -ally.ori*180/np.pi-90)
                    self.screen.blit(ally_reconn, (ally.pos[0] * MAP_SCALE, ally.pos[1] * MAP_SCALE))
                    
                    if self.draw_reconn_detect_range:
                        pygame.draw.circle(self.screen, (255, 0, 0), (ally.pos[0] * MAP_SCALE, ally.pos[1] * MAP_SCALE), self.args.fighter.reconnaissance.detect_range * MAP_SCALE, self.args.render_setting.circle_width)
                   
                elif ally.type == FIGHTER_TYPE['cannon']:
                    ally_cannon = pygame.transform.rotate(self.ally_cannon, -ally.ori*180/np.pi-90)
                    self.screen.blit(ally_cannon, ((ally.pos[0] - 7) * MAP_SCALE, (ally.pos[1] - 5.7) * MAP_SCALE))
                    
                    if self.draw_damage_range:
                        ally_points = self._get_pie_points(((ally.pos[0]) * MAP_SCALE, (ally.pos[1]) * MAP_SCALE), 
                                                            ally.ori,
                                                            self.args.fighter.cannon.damage_turn_range,
                                                         self.args.fighter.cannon.damage_range * MAP_SCALE)
                        pygame.gfxdraw.filled_polygon(self.screen, ally_points, (255, 0, 0, 96))

                    if self.draw_fighter_detect_range:
                        pygame.draw.circle(self.screen, (255, 0, 0, 32), (ally.pos[0] * MAP_SCALE, ally.pos[1] * MAP_SCALE), self.args.fighter.cannon.detect_range * MAP_SCALE, self.args.render_setting.circle_width)
                    
                else:
                    ally_missile = pygame.transform.rotate(self.ally_missile, -ally.ori*180/np.pi-90)
                    self.screen.blit(ally_missile, ((ally.pos[0] - 7) * MAP_SCALE, (ally.pos[1] - 5.7) * MAP_SCALE))
                    
                    if self.draw_fighter_detect_range:
                        pygame.draw.circle(self.screen, (255, 0, 0, 32), (ally.pos[0] * MAP_SCALE, ally.pos[1] * MAP_SCALE), self.args.fighter.missile.detect_range * MAP_SCALE, self.args.render_setting.circle_width)
                    if self.draw_damage_range:
                        surface = pygame.Surface(self.size, pygame.SRCALPHA)
                        pygame.draw.circle(surface, (255, 0, 0, 32), (ally.pos[0] * MAP_SCALE, ally.pos[1] * MAP_SCALE), self.args.fighter.missile.damage_range * MAP_SCALE, 0)
                        self.screen.blit(surface, (0, 0))

        for enemy in self.enemies:
            if enemy.alive:
                if enemy.type == FIGHTER_TYPE['reconnaissance']:
                    enemy_reconn = pygame.transform.rotate(self.enemy_reconn, -enemy.ori*180/np.pi-90)
                    self.screen.blit(enemy_reconn, (enemy.pos[0] * MAP_SCALE, enemy.pos[1] * MAP_SCALE))
                    
                    if self.draw_reconn_detect_range:
                        pygame.draw.circle(self.screen, (0, 0, 255, 32), (enemy.pos[0] * MAP_SCALE, enemy.pos[1] * MAP_SCALE), self.args.fighter.reconnaissance.detect_range * MAP_SCALE, self.args.render_setting.circle_width)
                   
                elif enemy.type == FIGHTER_TYPE['cannon']:
                    enemy_cannon = pygame.transform.rotate(self.enemy_cannon, -enemy.ori*180/np.pi-90)
                    self.screen.blit(enemy_cannon, ((enemy.pos[0] - 6) * MAP_SCALE, (enemy.pos[1] - 5.7) * MAP_SCALE))
                    
                    if self.draw_damage_range:
                        enemy_points = self._get_pie_points(((enemy.pos[0]) * MAP_SCALE, (enemy.pos[1]) * MAP_SCALE), 
                                                            np.array([enemy.ori]),
                                                            self.args.fighter.cannon.damage_turn_range,
                                                            self.args.fighter.cannon.damage_range * MAP_SCALE)
                        pygame.gfxdraw.filled_polygon(self.screen, enemy_points, (0, 0, 255, 96))

                    if self.draw_fighter_detect_range:
                        pygame.draw.circle(self.screen, (0, 0, 255, 32), (enemy.pos[0] * MAP_SCALE, enemy.pos[1] * MAP_SCALE), self.args.fighter.cannon.detect_range * MAP_SCALE, self.args.render_setting.circle_width)
            
                else:
                    enemy_missile = pygame.transform.rotate(self.enemy_missile, -enemy.ori*180/np.pi-90)
                    self.screen.blit(enemy_missile, ((enemy.pos[0] - 2) * MAP_SCALE, (enemy.pos[1] - 7.7) * MAP_SCALE))
                    
                    if self.draw_fighter_detect_range:
                        pygame.draw.circle(self.screen, (0, 0, 255, 32), (enemy.pos[0] * MAP_SCALE, enemy.pos[1] * MAP_SCALE), self.args.fighter.missile.detect_range * MAP_SCALE, self.args.render_setting.circle_width)
                    if self.draw_damage_range:
                        surface = pygame.Surface(self.size, pygame.SRCALPHA)
                        pygame.draw.circle(surface, (0, 0, 255, 32), (enemy.pos[0] * MAP_SCALE, enemy.pos[1] * MAP_SCALE), self.args.fighter.missile.damage_range * MAP_SCALE, 0)
                        self.screen.blit(surface, (0, 0))

        pygame.display.update()
        
        if save_pic:
            current_path = os.path.split(os.path.realpath(__file__))[0] + '/tmp/'
            pygame.image.save(self.screen, current_path+f'{self.image_name_count}.png')

            self.image_name_count += 1

    def _get_pie_points(self, pos, angle, angle_range, length):
        poses = [pos]
        pos = np.array(pos)

        angle_range /= 2

        angle_range_lower = (angle - angle_range)
        angle_range_upper = (angle + angle_range)

        lower_point = np.array([length * np.cos(angle_range_lower) + pos[0], length * np.sin(angle_range_lower) + pos[1]])
        poses.append(lower_point)
        
        data = np.arange(angle_range_lower, angle_range_upper, 0.01)
        for i in data:
            poses.append(np.array([length * np.cos(i) + pos[0], length * np.sin(i) + pos[1]]))

        higher_point = np.array([length * np.cos(angle_range_upper) + pos[0], length * np.sin(angle_range_upper) + pos[1]])
        poses.append(higher_point)

        return poses