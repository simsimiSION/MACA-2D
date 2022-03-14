
import numpy as np

from MACA.fighter.fighter_type import FIGHTER_TYPE

class CannonReconnHieraricalWrapper():
    def __init__(self, args, env):
        self.args = args
        self.n_agent = env.n_ally
        self.n_enemy = env.n_enemy

    def obs_wrapper(self, env):
        obses = {}
        for i, ally in enumerate(env.allies):
            obses[str(i+1)] = self._obs_fighter_wrapper(env, ally)
        return obses

    def action_wrapper(self, actions, env):
        encoded_action = []
        for i in actions.keys():
            if env.allies[int(i)-1].type == FIGHTER_TYPE['reconnaissance']:
                encoded_action.append([actions[i], 0])
            else:
                is_attack = actions[i][1]['is_attack']
                attack_target = actions[i][1]['attack_target']
                if is_attack:
                    encoded_action.append([actions[i][0], attack_target+1])
                else:
                    encoded_action.append([actions[i][0], 0])

        return encoded_action

    def reward_wrapper(self, env, game_status):
        rewards = {}
        for ally in env.allies:
            if ally.alive:
                if ally.type == FIGHTER_TYPE['reconnaissance']:
                    rewards[str(ally.id)] = self._reconn_reward_wrapper(ally, game_status)
                else:
                    rewards[str(ally.id)] = self._cannon_reward_wrapper(ally, game_status)
            else:
                rewards[str(ally.id)] = 0.0

        return rewards

    def done_wrapper(self, game_status, cnt):
        if game_status['n_alive_ally'] == 0 or game_status['n_alive_enemy'] == 0:
            return {"__all__": True}
        if cnt >= self.args.rl.max_time_step:
            return {"__all__": True}
        return {"__all__": False}

    def _obs_fighter_wrapper(self, env, fighter):
        """特征包含一下几个部分
            1. id
            2. position
            3. orientation
            4. bloods
            5. damage_range
            6. damage_turn_range
            7. detect info [pos, ori, bloods]
            8. last action
        """

        # self id
        id_ = np.zeros((self.n_agent, ), dtype=np.float)
        id_[fighter.id-1] = 1.0

        # self pos
        pos = fighter.pos - np.array([self.args.simulator.map_x_limit/2, self.args.simulator.map_y_limit/2])
        pos = pos / np.array([self.args.simulator.map_x_limit/2, self.args.simulator.map_y_limit/2])
        pos = pos.reshape(2, )

        # self ori
        ori = np.array([fighter.ori], dtype=np.float) / (np.pi * 2)
        ori = ori.reshape(1, )

        # self bloods
        bloods = np.array([fighter.bloods], dtype=np.float) / self.args.fighter.bloods
        bloods = bloods.reshape(1, )

        # damage_range
        damage_range = np.array([fighter.damage_range], dtype=np.float) / self.args.simulator.distance_normal_val
        damage_range = damage_range.reshape(1, )

        # damage_turn_range
        damage_turn_range = np.array([fighter.damage_turn_range], dtype=np.float) / np.pi
        damage_turn_range = damage_turn_range.reshape(1, )

        # detect ally info
        ally_infos = []
        for ally in env.allies:
            if ally.id != fighter.id:
                if ally.alive and ally.id in fighter.detect_allies:
                    ally_pos = ally.pos - np.array([self.args.simulator.map_x_limit/2, self.args.simulator.map_y_limit/2])
                    ally_pos = ally_pos / np.array([self.args.simulator.map_x_limit/2, self.args.simulator.map_y_limit/2])
                    ally_distance = np.linalg.norm(ally.pos-fighter.pos) / self.args.simulator.distance_normal_val
                    ally_ori = ally.ori / (np.pi * 2)
                    ally_bloods = ally.bloods / self.args.fighter.bloods

                    delta_pos = ally.pos-fighter.pos
                    theta = np.arctan2(delta_pos[1], delta_pos[0])
                    if theta < 0:
                        theta += np.pi * 2
                    
                    delta_theta = theta - fighter.ori
                    if delta_theta < -np.pi:
                        delta_theta += np.pi*2
                    if delta_theta > np.pi:
                        delta_theta -= np.pi*2
                    delta_theta /= np.pi 

                    # ally info
                    ally_infos.extend([
                        ally_pos[0],
                        ally_pos[1],
                        ally_distance,
                        delta_theta,
                        ally_ori,
                        ally_bloods,
                    ])
                else:
                    ally_infos.extend([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        ally_infos = np.array(ally_infos, dtype=np.float)

        # detect enemy info
        enemy_infos = []
        for enemy in env.enemies:
            if enemy.alive and enemy.id in fighter.detect_enemies:
                enemy_pos = enemy.pos - np.array([self.args.simulator.map_x_limit/2, self.args.simulator.map_y_limit/2])
                enemy_pos = enemy_pos / np.array([self.args.simulator.map_x_limit/2, self.args.simulator.map_y_limit/2])
                enemy_distance = np.linalg.norm(enemy.pos-fighter.pos) / self.args.simulator.distance_normal_val
                enemy_ori = enemy.ori / (np.pi * 2)
                enemy_bloods = enemy.bloods / self.args.fighter.bloods

                delta_pos = enemy.pos-fighter.pos
                theta = np.arctan2(delta_pos[1], delta_pos[0])
                if theta < 0:
                    theta += np.pi * 2
                
                delta_theta = theta - fighter.ori
                if delta_theta < -np.pi:
                    delta_theta += np.pi*2
                if delta_theta > np.pi:
                    delta_theta -= np.pi*2
                delta_theta /= np.pi 

                # enemy info
                enemy_infos.extend([
                    enemy_pos[0],
                    enemy_pos[1],
                    enemy_distance,
                    delta_theta,
                    enemy_ori,
                    enemy_bloods,
                ])
            else:
                enemy_infos.extend([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        enemy_infos = np.array(enemy_infos, dtype=np.float)

        fighter_obs = np.concatenate(
            [
             pos,
             ori,
             bloods,
             damage_range,
             damage_turn_range,
             ally_infos,
             enemy_infos,
            ],
            axis=0)
        
        if fighter.alive:
            return fighter_obs
        return np.zeros_like(fighter_obs)

    def _cannon_reward_wrapper(self, fighter, game_status):
        attack_reward = game_status['ally_info'][fighter.id]['damage_val'] * self.args.rl.reward.cannon_attack
        time_penalty = float(self.args.rl.reward.time_penalty)

        final_reward = 0
        if game_status['n_alive_ally'] == 0 and game_status['n_alive_enemy'] == 0: # tier
            final_reward = self.args.rl.reward.tier
        elif game_status['n_alive_ally'] == 0:
            final_reward = self.args.rl.reward.lose
        elif game_status['n_alive_enemy'] == 0:
            final_reward = self.args.rl.reward.win

        return attack_reward + time_penalty + final_reward
    
    def _reconn_reward_wrapper(self, fighter, game_status):
        detect_reward = len(fighter.detect_enemies) * self.args.rl.reward.reconn_detect
        time_penalty = float(self.args.rl.reward.time_penalty)

        final_reward = 0
        if game_status['n_alive_ally'] == 0 and game_status['n_alive_enemy'] == 0: # tier
            final_reward = self.args.rl.reward.tier
        elif game_status['n_alive_ally'] == 0:
            final_reward = self.args.rl.reward.lose
        elif game_status['n_alive_enemy'] == 0:
            final_reward = self.args.rl.reward.win
        return detect_reward + time_penalty + final_reward
    
