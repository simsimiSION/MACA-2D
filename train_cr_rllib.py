
import ray
from ray import tune
from ray.tune import register_env

from MACA.env.cannon_reconn_hierarical import CannonReconnHieraricalEnv
from RL.callbacks.cr_callback import CRCallback



def main():

    # test env
    cr_env = CannonReconnHieraricalEnv(None)

    # register env
    register_env(
        'cr_env_hier',
        lambda config: CannonReconnHieraricalEnv(config)
    )

    # multi-agent policies
    policies = {
        str(i): (None,
                 cr_env.observation_spaces[i],
                 cr_env.action_spaces[i],
                 {"agent_id": i}) for i in range(2)
    }

    def policy_mapping_fn(agent_id):
        if int(agent_id)-1 < cr_env.args.env.n_ally_reconn:
            return '0'
        else:
            return '1'    
    
    # rllib config
    config = {
        "env": "cr_env_hier",
        "multiagent": {
            "policies": policies,
            "policy_mapping_fn": policy_mapping_fn,
        },
        "framework": "torch",
        "train_batch_size": 15000,
        "sgd_minibatch_size": 512,
        "entropy_coeff": 0.0,
        "lr": 1e-5, #1e-5
        "num_workers": 2,
        "num_gpus": 1.0,
        "callbacks": CRCallback,
    }

    # run rllib
    ray.init()
    tune.run(
        "PPO",
        config=config,
        checkpoint_at_end=True,
        checkpoint_freq=50,
        local_dir='resource/',
        #restore='',
        export_formats=['model', 'checkpoint'],
        verbose=1
    )

if __name__ == '__main__':
    main()