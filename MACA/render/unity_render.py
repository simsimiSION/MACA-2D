
import os
import pygame
import numpy as np

import socket
import time
import json

from MACA.fighter.fighter_type import FIGHTER_TYPE

class UnityRender():
    def __init__(self, args, allies, enemies):
        self.args = args
        self.allies = allies
        self.enemies = enemies
        self.draw_detect_range = args.render_setting.draw_detect_range
        self.draw_damage_range = args.render_setting.draw_damage_range

        HOST = '127.0.0.1'
        PORT = 42875

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(30)
        self.client.connect((HOST, PORT))



    def render(self, save_pic=False):
        total_datas = {}

        for ally in self.allies:  
            data = {
                "id": ally.id,
                "side": 1,
                "alive": ally.alive,
                "pos_x": ally.pos[0] + 500,
                "pos_y": 50,
                "pos_z": ally.pos[1],
                "angle_x": 0.0,
                "angle_y": -ally.ori*180/np.pi + 90,
                "angle_z": 0.0,
            }
            total_datas[data["id"]] = data
            
        for enemy in self.enemies:
            data = {
                "id": 100+enemy.id,
                "side": 2,
                "alive": enemy.alive,
                "pos_x": enemy.pos[0] + 500,
                "pos_y": 50,
                "pos_z": enemy.pos[1],
                "angle_x": 0.0,
                "angle_y": -enemy.ori*180/np.pi + 90,
                "angle_z": 0.0,
            }
            total_datas[data["id"]] = data

        json_data = json.dumps(total_datas)
        sendBytes = self.client.send(json_data.encode())

        
        