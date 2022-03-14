
import time

from MACA.env.cannon_reconn_hierarical import CannonReconnHieraricalEnv
from MACA.render.gif_generator import gif_generate

if __name__ == '__main__':
    env = CannonReconnHieraricalEnv({"render": True})

    env.reset()

    done = False
    step = 0
    total_damage = 0
    while not done:
        time.sleep(0.05)

        actions = {
            '1': [0.0], 
            '2': [0.0], 
            '3': [0.0, {'is_attack': 1, 'attack_target': 2}], 
            '4': [0.0, {'is_attack': 1, 'attack_target': 2}], 
            '5': [0.0, {'is_attack': 1, 'attack_target': 2}], 
            '6': [0.0, {'is_attack': 1, 'attack_target': 2}], 
            '7': [0.0, {'is_attack': 1, 'attack_target': 2}]
        }
    
        obs, reward, dones, info = env.step(actions)
        env.render(save_pic=True)
        done = dones['__all__']

        step += 1
        total_damage += sum([item[1] for item in info['1']['ally_damage'].items()])
    gif_generate('test.gif')
    print(f'total damage: {total_damage}')

        
        