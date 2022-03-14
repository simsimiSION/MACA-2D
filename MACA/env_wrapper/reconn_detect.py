
import numpy as np
import networkx as nx

from MACA.env_wrapper.cannon_reconn_hierarical import CannonReconnHieraricalWrapper


class ReconnDetectAdjWrapper(CannonReconnHieraricalWrapper):
    def __init__(self, args, env):
        super(ReconnDetectAdjWrapper, self).__init__(args, env)
    
    def obs_wrapper(self, env):
        obses = {}

        adj = self._gen_adj(env)

        for i, ally in enumerate(env.allies):
            obses[str(i+1)] = np.concatenate([self._obs_fighter_wrapper(env, ally), adj], axis=-1)
        return obses

    def reward_wrapper(self, env, game_status):
        total_detect_list = []
        for ally in env.allies:
            if ally.alive:
                total_detect_list.extend(ally.detect_enemies)
        total_detect_list = list(set(total_detect_list))
        
        total_detect_reward = len(total_detect_list) * self.args.rl.reward.reconn_detect
        time_penalty = float(self.args.rl.reward.time_penalty)

        rewards = {}
        for ally in env.allies:
            if ally.alive:
                rewards[str(ally.id)] = total_detect_reward + time_penalty
            else:
                rewards[str(ally.id)] = 0.0

        return rewards

    def _gen_adj(self, env, top_k=2):
        def _normalize(A, symmetric=True):
            A = A + np.eye(A.shape[0])

            d = A.sum(1)
            if symmetric:
                D = np.diag(np.power(d, -0.5))
                return D @ A @ D
            else:
                D = np.diag(np.power(d, -1))
                return D @ A

        positions = []
        for ally in env.allies:
            positions.append(ally.pos.reshape(1, -1))
        positions = np.concatenate(positions, axis=0)

        G = nx.Graph()
        for i, ally in enumerate(env.allies):
            if ally.alive:
                pos_i = ally.pos.reshape(1, -1)

                # 计算欧式距离
                dist = np.linalg.norm(positions - pos_i, axis=-1)

                # 选取除自己外的top_k最近节点标号
                top_k_id = dist.argsort()[1:top_k+1]

                # 将对应连接添加到图中
                for j in top_k_id: G.add_edge(i, j)

        adj_matrix = np.array(nx.adjacency_matrix(G, nodelist=range(len(env.allies))).todense())
        adj_matrix = _normalize(adj_matrix)
        return adj_matrix.reshape(-1)

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
                fake_enemy_pos = enemy.pos + np.random.uniform(-50, 50, size=(2))
                enemy_pos = fake_enemy_pos / np.array([self.args.simulator.map_x_limit/2, self.args.simulator.map_y_limit/2])
                enemy_distance = np.linalg.norm(fake_enemy_pos-fighter.pos) / self.args.simulator.distance_normal_val

                delta_pos = fake_enemy_pos-fighter.pos
                theta = np.arctan2(delta_pos[1], delta_pos[0])
                if theta < 0:
                    theta += np.pi * 2
                
                delta_theta = theta - fighter.ori
                if delta_theta < -np.pi:
                    delta_theta += np.pi*2
                if delta_theta > np.pi:
                    delta_theta -= np.pi*2
                delta_theta /= np.pi 

                enemy_infos.extend([enemy_pos[0], enemy_pos[1], enemy_distance, delta_theta, 0.0, 0.0])

        enemy_infos = np.array(enemy_infos, dtype=np.float)

        fighter_obs = np.concatenate(
            [
             id_,
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

    def _reconn_reward_wrapper(self, fighter, game_status):
        detect_reward = len(fighter.detect_enemies) * self.args.rl.reward.reconn_detect
        time_penalty = float(self.args.rl.reward.time_penalty)

        return detect_reward + time_penalty      