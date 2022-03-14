

from ray.rllib.agents.callbacks import DefaultCallbacks 

# For Tensorboard可视化
class CRCallback(DefaultCallbacks):
    def on_episode_start(self, *, worker, base_env, policies, episode, env_index, **kwargs):
        self.total_damage = 0.0

    def on_episode_step(self, *, worker, base_env, episode, env_index, **kwargs):
        if episode.last_info_for('1') is not None:
            if 'ally_damage' in episode.last_info_for('1'):
                self.total_damage += sum([item[1] for item in  episode.last_info_for('1')['ally_damage'].items()])

    def on_episode_end(self, *, worker, base_env, policies, episode, env_index, **kwargs):
        if episode.last_info_for('1') is not None:
            episode.custom_metrics['n_alive_enemy'] = episode.last_info_for('1')['n_alive_enemy']
            episode.custom_metrics['delta_action'] = episode.last_info_for('1')['delta_action']
            episode.custom_metrics['total_damage'] = self.total_damage
