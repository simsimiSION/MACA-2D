
import numpy as np 

from MACA.fighter.fighter_type import FIGHTER_TYPE
from MACA.fighter.base import BaseFighter

class ReconnaissanceFighter(BaseFighter):
    def __init__(self, args):
        super(ReconnaissanceFighter, self).__init__(args)
        self.type = FIGHTER_TYPE['reconnaissance']

    def initialize(self, base_info):
        BaseFighter.initialize(self, base_info)

        # 获取目标pos
        if self.side == 0:
            self.script_target_pos = np.array([
                self.args.simulator.map_x_limit * 0.75,
                self.initial_pos[1]
            ])    
        elif self.side == 1:
            self.script_target_pos = np.array([
                self.args.simulator.map_x_limit * 0.25,
                self.initial_pos[1]
            ])
        
    def script_action(self, enemies):
        if self.alive:
            target_pos = self.script_target_pos

            if len(self.detect_enemies) != 0:
                target_pos = enemies[self.detect_enemies[0]-1].pos

            # calc direct
            delta_pos = target_pos - self.pos
            
            desire_theta = np.arctan2(delta_pos[1], delta_pos[0])
            if desire_theta < 0:
                desire_theta += np.pi * 2

            delta_theta = desire_theta - self.ori

            direct = np.clip(delta_theta, -self.turn_range, self.turn_range)

            return [direct, 0]
        return [0, 0]