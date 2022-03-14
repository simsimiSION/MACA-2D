
import numpy as np

from MACA.fighter.fighter_type import FIGHTER_TYPE

class BaseSimulator():
    def __init__(self, args, allies, enemies):
        self.args = args
        
        # fighter
        self.allies = allies
        self.enemies = enemies
        self.n_ally = len(allies)
        self.n_enemy = len(enemies)

        # get ally & enemy fighter type info
        self.n_allies_reconnaissance = 0
        self.n_allies_other = 0
        for ally in self.allies:
            if ally.type == FIGHTER_TYPE['reconnaissance']:
                self.n_allies_reconnaissance += 1
            else:
                self.n_allies_other += 1

        self.n_enemies_reconnaissance = 0
        self.n_enemies_other = 0
        for enemy in self.enemies:
            if enemy.type == FIGHTER_TYPE['reconnaissance']:
                self.n_enemies_reconnaissance += 1
            else:
                self.n_enemies_other += 1

        # simulator info
        self.dt = args.simulator.dt

        # position limiation
        self.allies_reconnaissance_x_bias = 100
        self.allies_reconnaissance_y_resolution = args.simulator.map_y_limit / (self.n_allies_reconnaissance + 1)
        self.allies_other_x_bias = 200
        self.allies_other_y_resolution = args.simulator.map_y_limit / (self.n_allies_other + 1)

        self.enemies_reconnaissance_x_bias = args.simulator.map_x_limit - 100
        self.enemies_reconnaissance_y_resolution = args.simulator.map_y_limit / (self.n_enemies_reconnaissance + 1) 
        self.enemies_other_x_bias = args.simulator.map_x_limit - 200
        self.enemies_other_y_resolution = args.simulator.map_y_limit / (self.n_enemies_other + 1) 

    def initialize(self, random_side=False):
        # random fighter position side
        is_flip = 0
        if random_side:
            is_flip = np.random.randint(0, 2)

        if is_flip:
            allies_reconnaissance_x_bias = self.args.simulator.map_x_limit - self.allies_reconnaissance_x_bias
            allies_other_x_bias = self.args.simulator.map_x_limit - self.allies_other_x_bias
            enemies_reconnaissance_x_bias = self.args.simulator.map_x_limit - self.enemies_reconnaissance_x_bias
            enemies_other_x_bias = self.args.simulator.map_x_limit - self.enemies_other_x_bias
        else:
            allies_reconnaissance_x_bias = self.allies_reconnaissance_x_bias
            allies_other_x_bias = self.allies_other_x_bias
            enemies_reconnaissance_x_bias = self.enemies_reconnaissance_x_bias
            enemies_other_x_bias = self.enemies_other_x_bias
        
        # ally initialize
        for i, ally in enumerate(self.allies):

            # pos initialize
            if ally.type == FIGHTER_TYPE['reconnaissance']:
                pos = np.array([allies_reconnaissance_x_bias, self.allies_reconnaissance_y_resolution*(i+1)])
            else:
                pos = np.array([allies_other_x_bias, self.allies_other_y_resolution*(i+1-self.n_allies_reconnaissance)]) + np.random.uniform(-1, 1, size=(2)) * self.args.simulator.random_limit

            # ori initialize
            if is_flip:
                ori = np.pi
                side = 1
            else:
                ori = 0.0
                side = 0

            # spec info
            spec_info = self._get_specifical_fighter_info(ally.type)

            base_info = {
                'id': i+1,
                'side': side,
                'pos': pos,
                'ori': ori,
                'speed': self.args.fighter.speed,
                'bloods': self.args.fighter.bloods,
                'turn_range': self.args.fighter.turn_range,
                'map_x_limit': self.args.simulator.map_x_limit,
                'map_y_limit': self.args.simulator.map_y_limit,
                'detect_range': spec_info['detect_range'],
                'damage': spec_info['damage'],
                'damage_range': spec_info['damage_range'],
                'damage_turn_range': spec_info['damage_turn_range'],
            }

            # initialize
            ally.initialize(base_info)

        # enemy initialize
        for i, enemy in enumerate(self.enemies):
            
            # pos initialize
            if enemy.type == FIGHTER_TYPE['reconnaissance']:
                pos = np.array([enemies_reconnaissance_x_bias, self.enemies_reconnaissance_y_resolution*(i+1)])
            else:
                pos = np.array([enemies_other_x_bias, self.enemies_other_y_resolution*(i+1-self.n_enemies_reconnaissance)]) + np.random.uniform(-1, 1, size=(2)) * self.args.simulator.random_limit

            # ori initialize
            if is_flip:
                ori = 0.0
                side = 0
            else:
                ori = np.pi
                side = 1

            # spec info
            spec_info = self._get_specifical_fighter_info(enemy.type)

            base_info = {
                'id': i+1,
                'side': side,
                'pos': pos,
                'ori': ori,
                'speed': self.args.fighter.speed,
                'bloods': self.args.fighter.bloods,
                'turn_range': self.args.fighter.turn_range,
                'map_x_limit': self.args.simulator.map_x_limit,
                'map_y_limit': self.args.simulator.map_y_limit,
                'detect_range': spec_info['detect_range'],
                'damage': spec_info['damage'],
                'damage_range': spec_info['damage_range'],
                'damage_turn_range': spec_info['damage_turn_range'],
            }

            # initialize
            enemy.initialize(base_info)
        
        return self.get_game_status(None)

    def step(self, actions):
        # update detect info
        self._update_detect_list()
        self._share_reconn_detect_to_other()

        # enemy script to get actions
        enemy_actions = []
        for enemy in self.enemies:
            enemy_actions.append(enemy.script_action(self.allies))

        # get be_attack_list
        enemy_be_attack_list, ally_attack_val = self._convert_action_to_be_attacked_list(self.allies, self.enemies, actions)
        ally_be_attack_list, _ = self._convert_action_to_be_attacked_list(self.enemies, self.allies, enemy_actions)
        
        # ally take action
        for ally, action, ally_be_attack in zip(self.allies, actions, ally_be_attack_list):
            direct = action[0]
            attack = action[1]
            ally.step(direct, ally_be_attack, attack, attack_bias=self.args.fighter.attack_bias)
        
        # enemy take action
        for enemy, action, enemy_be_attack in zip(self.enemies, enemy_actions, enemy_be_attack_list):
            direct = action[0]
            attack = action[1]
            enemy.step(direct, enemy_be_attack, attack)
        
        return self.get_game_status(ally_attack_val)
    
    def get_game_status(self, ally_attack_val):
        game_status = {}

        n_alive_ally = 0
        n_alive_enemy = 0

        game_status['ally_info'] = {}
        for i, ally in enumerate(self.allies):
            game_status['ally_info'][ally.id] = {}
            game_status['ally_info'][ally.id]['alive'] = ally.alive
            game_status['ally_info'][ally.id]['blood'] = ally.bloods
            game_status['ally_info'][ally.id]['pos'] = ally.pos
            game_status['ally_info'][ally.id]['ori'] = ally.ori
            if ally_attack_val:
                game_status['ally_info'][ally.id]['damage_val'] = ally_attack_val[i]

            if ally.alive:
                n_alive_ally += 1

        game_status['enemy_info'] = {}
        for enemy in self.enemies:
            game_status['enemy_info'][enemy.id] = {}
            game_status['enemy_info'][enemy.id]['alive'] = enemy.alive
            game_status['enemy_info'][enemy.id]['blood'] = enemy.bloods
            game_status['enemy_info'][enemy.id]['pos'] = enemy.pos
            game_status['enemy_info'][enemy.id]['ori'] = enemy.ori

            if enemy.alive:
                n_alive_enemy += 1
        
        game_status['n_alive_ally'] = n_alive_ally
        game_status['n_alive_enemy'] = n_alive_enemy

        return game_status

    def _convert_action_to_be_attacked_list(self, fighters, enemy_fighters, actions):
        be_attack_list = [[] for _ in range(len(enemy_fighters))] # 敌方fighter被攻击血量计算
        fighter_damage_val = [0 for _ in range(len(fighters))] #fighter攻击量计算

        for i, (fighter, action) in enumerate(zip(fighters, actions)):
            attack_target = action[1]
            if fighter.alive and attack_target in fighter.detect_enemies and self._can_attack(fighter, enemy_fighters[attack_target-1]):
                be_attack_list[attack_target-1].append(fighter.damage)
                fighter_damage_val[i] = fighter.damage

        return be_attack_list, fighter_damage_val

    def _update_detect_list(self):
        """更新每个fighter侦测的ally和enemy
        """
        # ally
        for ally in self.allies:
            d_as = []
            for d_a in self.allies:
                if d_a.alive and np.linalg.norm(ally.pos-d_a.pos) < ally.detect_range:
                    d_as.append(d_a.id)
            
            d_es = []
            for d_e in self.enemies:
                if d_e.alive and np.linalg.norm(ally.pos-d_e.pos) < ally.detect_range:
                    d_es.append(d_e.id)
            
            # update info
            ally.detect_allies = d_as
            ally.detect_enemies = d_es
        
        # enemy
        for enemy in self.enemies:
            d_as = []
            for d_a in self.allies:
                if d_a.alive and np.linalg.norm(enemy.pos-d_a.pos) < enemy.detect_range:
                    d_as.append(d_a.id)
            
            d_es = []
            for d_e in self.enemies:
                if d_e.alive and np.linalg.norm(enemy.pos-d_e.pos) < enemy.detect_range:
                    d_es.append(d_e.id)

            enemy.detect_allies = d_es
            enemy.detect_enemies = d_as
    
    def _share_reconn_detect_to_other(self):
        # ally detect处理
        ally_reconn_detect_allies = []
        ally_reconn_detect_enemies = []
        for ally in self.allies:
            # 获取reconnaissance检测的并集
            if ally.type == FIGHTER_TYPE['reconnaissance']:
                ally_reconn_detect_allies = list(set(ally.detect_allies).union(set(ally_reconn_detect_allies)))
                ally_reconn_detect_enemies = list(set(ally.detect_enemies).union(set(ally_reconn_detect_enemies)))
        
        for ally in self.allies:
            # 将reconnaissance检测的并集于其他fighter的检测于并集
            if ally.type != FIGHTER_TYPE['reconnaissance']:
                ally.detect_allies = list(set(ally.detect_allies).union(set(ally_reconn_detect_allies)))
                ally.detect_enemies = list(set(ally.detect_enemies).union(set(ally_reconn_detect_enemies)))

        # enemy detect处理
        enemy_reconn_detect_allies = []
        enemy_reconn_detect_enemies = []
        for enemy in self.enemies:
            # 获取reconnaissance检测的并集
            if enemy.type == FIGHTER_TYPE['reconnaissance']:
                enemy_reconn_detect_allies = list(set(enemy.detect_allies).union(set(enemy_reconn_detect_allies)))
                enemy_reconn_detect_enemies = list(set(enemy.detect_enemies).union(set(enemy_reconn_detect_enemies)))
        
        for enemy in self.enemies:
            # 将reconnaissance检测的并集于其他fighter的检测于并集
            if enemy.type != FIGHTER_TYPE['reconnaissance']:
                enemy.detect_allies = list(set(enemy.detect_allies).union(set(enemy_reconn_detect_allies)))
                enemy.detect_enemies = list(set(enemy.detect_enemies).union(set(enemy_reconn_detect_enemies)))

    def _get_specifical_fighter_info(self, fighter_type):
        """获取fighter info
        """
        spec_info = {}
        if fighter_type == FIGHTER_TYPE['cannon']:
            spec_info = {
                'detect_range': self.args.fighter.cannon.detect_range,
                'damage': self.args.fighter.cannon.damage,
                'damage_range': self.args.fighter.cannon.damage_range,
                'damage_turn_range': self.args.fighter.cannon.damage_turn_range,
            }
        elif fighter_type == FIGHTER_TYPE['missile']:
            spec_info = {
                'detect_range': self.args.fighter.missile.detect_range,
                'damage': self.args.fighter.missile.damage,
                'damage_range': self.args.fighter.missile.damage_range,
                'damage_turn_range': self.args.fighter.missile.damage_turn_range,
            }
        elif fighter_type == FIGHTER_TYPE['reconnaissance']:
            spec_info = {
                'detect_range': self.args.fighter.reconnaissance.detect_range,
                'damage': self.args.fighter.reconnaissance.damage,
                'damage_range': self.args.fighter.reconnaissance.damage_range,
                'damage_turn_range': self.args.fighter.reconnaissance.damage_turn_range,
            }
        else:
            raise Exception(f'Unknown fighter_type: {fighter_type} !!!')
        return spec_info

    def _can_attack(self, fighter, be_attacked_fighter):
        in_attack_distance_range = self._calc_distance(fighter, be_attacked_fighter) <= fighter.damage_range

        delta_pos = be_attacked_fighter.pos - fighter.pos
        theta = np.arctan2(delta_pos[1], delta_pos[0])
        if theta < 0:
            theta += np.pi * 2
        
        delta_theta = theta - fighter.ori
        if delta_theta < -np.pi:
            delta_theta += np.pi*2
        if delta_theta > np.pi:
            delta_theta -= np.pi*2

        delta_theta = np.abs(delta_theta)
        in_attack_turn_range = (delta_theta <= fighter.damage_turn_range)

        if in_attack_distance_range and in_attack_turn_range:
            return True
        return False


    def _calc_distance(self, fighter1, fighter2):
        return np.linalg.norm(fighter1.pos-fighter2.pos)

