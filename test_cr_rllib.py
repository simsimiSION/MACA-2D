
import os
import numpy as np
import pickle
import time

import ray
from ray.rllib.utils.framework import try_import_torch
from ray.rllib.models import ModelCatalog
from ray.rllib.agents.ppo.ppo import DEFAULT_CONFIG
from ray.rllib.agents.ppo.ppo_torch_policy import PPOTorchPolicy as LoadPolicy
torch, nn = try_import_torch()

from MACA.env.cannon_reconn_hierarical import CannonReconnHieraricalEnv
from MACA.utils.setting import get_args
from MACA.render.gif_generator import gif_generate

class Agent():
    def __init__(self, load_path, observation_space, action_space):
        self.detector_prep = ModelCatalog.get_preprocessor_for_space(observation_space[0])
        self.fighter_prep = ModelCatalog.get_preprocessor_for_space(observation_space[1])
        detector_flat_obs_space = self.detector_prep.observation_space
        fighter_flat_obs_space = self.fighter_prep.observation_space

        config = DEFAULT_CONFIG.copy()
        self.args = get_args()

        self.policies = {}
        self.policies['0'] = LoadPolicy(detector_flat_obs_space, action_space[0], config)
        self.policies['1'] = LoadPolicy(fighter_flat_obs_space, action_space[1], config)

        objs = pickle.load(open(load_path, "rb"))
        objs = pickle.loads(objs["worker"])
        state = objs["state"]

        for i in range(0, 2):
            state[str(i)].pop('_optimizer_variables')
            self.policies[str(i)].set_weights(state[str(i)])

    def act(self, obs):  
        act_dict = {}
        
        for i in range(1, 3):
            obs_i = self.detector_prep.transform(obs[str(i)])
            act = self.policies['0'].compute_actions([obs_i], explore=False)
            act = act[0][0]

            act = np.clip(act, -self.args.fighter.turn_range, self.args.fighter.turn_range)
            act_dict[str(i)] = act

        for i in range(3, 8):
            obs_i = self.fighter_prep.transform(obs[str(i)])

            act = self.policies['1'].compute_actions([obs_i], explore=True)
            direct = act[0][0]
            attack = act[0][1]['attack'][0]

            direct = np.clip(direct, -self.args.fighter.turn_range, self.args.fighter.turn_range)
            act_dict[str(i)] = (direct, {'attack': attack})

        return act_dict



def main():
    cr_env = CannonReconnHieraricalEnv({'render': True})

    # 设定路径
    path = ''
    agent = Agent(path, cr_env.observation_spaces, cr_env.action_spaces)
    
    episode = 0
    while True:
        state = cr_env.reset()
        done = False
        total_reward = 0.
        episode += 1
        step = 0
        total_damage = 0
        while not done:
            time.sleep(0.02)
            action = agent.act(state)

            state, reward, dones, info = cr_env.step(action)
            cr_env.render(save_pic=True)
            done = dones['__all__']

            total_reward += sum([reward[str(i)] for i in range(1, 6)])
            total_damage += sum([item[1] for item in info['1']['ally_damage'].items()])

            step += 1

        print("episode: {}, time_step: {}, total_reward: {}, total_damage: {}".format(episode, step, total_reward, total_damage))
        gif_generate('demo.gif')
        break


if __name__ == '__main__':
    main()