
from enum import Enum
import numpy as np

from MACA.fighter.fighter_type import FIGHTER_TYPE

class BaseFighter():
    def __init__(self, args):
        self.args = args

        self.dt = args.simulator.dt

        # 位置相关信息
        self.id = None
        self.type = FIGHTER_TYPE['base']
        self.side = None
        self.alive = None
        self.pos = None
        self.initial_pos = None
        self.ori = None
        self.speed = None
        self.bloods = None

        # 转交范围
        self.turn_range = None

        # 地图信息
        self.map_size = None

        # 探测范围
        self.detect_range = None

        # 探测的ally和enemy
        self.detect_allies = []
        self.detect_enemies = []

        # 攻击相关信息
        self.damage = None
        self.damage_range = None
        self.damage_turn_range = None

        # last action
        self.last_action = [0.0, 0]
    
    def initialize(self, base_info):
        self.id = base_info['id']
        self.side = base_info['side']
        self.alive = True

        self.pos = base_info['pos']
        self.initial_pos = [self.pos[0], self.pos[1]]
        self.ori = base_info['ori']
        self.speed = base_info['speed']
        self.bloods = base_info['bloods']

        self.turn_range = base_info['turn_range']

        self.map_size = [base_info['map_x_limit'], base_info['map_y_limit']]

        # 探测范围
        self.detect_range = base_info['detect_range']

        # 攻击相关信息
        self.damage = base_info['damage']
        self.damage_range = base_info['damage_range']
        self.damage_turn_range = base_info['damage_turn_range']

        # 检测清零
        self.detect_allies = []
        self.detect_enemies = []

        # last action
        self.last_action = [0.0, 0]

    def step(self, direct, be_attacked, attack, attack_bias=1.0):
        if self.alive:
            # 转角限制
            direct = np.clip(direct, -self.turn_range, self.turn_range)
            self.ori += direct
            self.ori = self._angle_clip(self.ori)

            # 位置更新
            bias_x = np.cos(self.ori) * self.dt * self.speed
            bias_y = np.sin(self.ori) * self.dt * self.speed
            self.pos[0] += bias_x
            self.pos[1] += bias_y

            # 位置限制
            self.pos[0] = np.clip(self.pos[0], 0, self.map_size[0])
            self.pos[1] = np.clip(self.pos[1], 0, self.map_size[1])
            
            # 被攻击更新
            self.bloods -= sum(be_attacked) * attack_bias

            # 血量限制
            if self.bloods < 0.0:
                self.bloods = 0.0
            if self.bloods == 0.0:
                self.alive = False

            # last action recorded
            self.last_action = [direct, attack]

    def script_action(self, enemies):
        raise NotImplementedError

    def _angle_clip(self, angle):
        while angle > 2 * np.pi:
            angle -= 2 * np.pi
        while angle < 0:
            angle += 2 * np.pi
        return angle