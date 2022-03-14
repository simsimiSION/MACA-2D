
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import *


class StageGen():
    def __init__(self, stage_len=50):
        self.stage_len = stage_len

        self.allies_info = {}
        self.enemies_info = {}

    def step(self, allies, enemies, step):
        
        # if step % self.stage_len == 0:
        #     return

        for ally in allies:
            # add new ally
            if ally.id not in self.allies_info:
                self.allies_info[ally.id] = []

            if ally.alive:
                if isinstance(ally.ori, np.ndarray):
                    ori = ally.ori[0]
                else:
                    ori = ally.ori
                self.allies_info[ally.id].append(
                    [step, ally.pos[0], ally.pos[1], float(ori)]
                )

        for enemy in enemies:
            # add new enemy
            if enemy.id not in self.enemies_info:
                self.enemies_info[enemy.id] = []
            
            if enemy.alive:
                if isinstance(enemy.ori, np.ndarray):
                    ori = enemy.ori[0]
                else:
                    ori = enemy.ori
                self.enemies_info[enemy.id].append(
                    [step, enemy.pos[0], enemy.pos[1], float(ori)]
                )
    
    def plot(self,):
        print('----------------------------------------')
        print('========== stage plot ==========')
        plt.figure(figsize=(8, 5))
        ax = plt.gca()

        # font 
        content_font = FontProperties(
            fname='/Users/zhoutianze/miniforge3/lib/python3.9/site-packages/matplotlib/mpl-data/fonts/ttf/SimHei.ttf',
            size=13
        )

        title_font = FontProperties(
            fname='/Users/zhoutianze/miniforge3/lib/python3.9/site-packages/matplotlib/mpl-data/fonts/ttf/SimHei.ttf',
            size=15
        )

        for ally_key in self.allies_info:
            ally_data = self.allies_info[ally_key]
            ori_ally_data = ally_data[::self.stage_len]

            ally_data = np.array(ally_data)
            ax.plot(ally_data[::5, 1], ally_data[::5, 2], c='r', linewidth=2)
            
            # arrow
            for ori_data in ori_ally_data:
                ax.arrow(ori_data[1], 
                          ori_data[2], 
                          np.cos(ori_data[3]) * 20, 
                          np.sin(ori_data[3]) * 20, 
                          shape="full",
                          head_width=5.0)
                ax.text(ori_data[1]-10, 
                         ori_data[2]+10, 
                         ori_data[0], 
                         fontsize=6)

        for enemy_key in self.enemies_info:
            enemy_data = self.enemies_info[enemy_key]
            enemy_data = np.array(enemy_data)[::40]
            n_enemy_data = enemy_data.shape[0]

            for i in range(0, n_enemy_data, n_enemy_data-1):
                plt.scatter(enemy_data[i, 1], 
                            enemy_data[i, 2], 
                            c='b', 
                            s=5+15*i/n_enemy_data,
                            alpha=max(0.1, (i/n_enemy_data)**2))
            plt.plot(enemy_data[:, 1], 
                     enemy_data[:, 2], 
                     c='b', 
                     linewidth=0.7,
                     alpha=0.13)

        ax.grid(alpha=0.2, linestyle='--',)
        ax.set_xlim(-50, 850)
        ax.set_ylim(-50, 550)
        ax.invert_yaxis()
        ax.set_title('动态目标场景轨迹图', FontProperties=title_font)
        ax.set_xlabel('x轴坐标', FontProperties=content_font)
        ax.set_ylabel('y轴坐标', FontProperties=content_font)
        plt.show()


class StageGenPIT():
    def __init__(self, stage_len=50):
        self.stage_len = stage_len

        self.allies_info = {}
        self.enemies_info = {}

    def step(self, allies, enemies, step):
        
        # if step % self.stage_len == 0:
        #     return

        for ally in allies:
            # add new ally
            if ally.id not in self.allies_info:
                self.allies_info[ally.id] = []

            if ally.alive:
                if isinstance(ally.ori, np.ndarray):
                    ori = ally.ori[0]
                else:
                    ori = ally.ori
                self.allies_info[ally.id].append(
                    [step, ally.pos[0], ally.pos[1], float(ori)]
                )

        for enemy in enemies:
            # add new enemy
            if enemy.id not in self.enemies_info:
                self.enemies_info[enemy.id] = []
            
            if enemy.alive:
                if isinstance(enemy.ori, np.ndarray):
                    ori = enemy.ori[0]
                else:
                    ori = enemy.ori
                self.enemies_info[enemy.id].append(
                    [step, enemy.pos[0], enemy.pos[1], float(ori)]
                )
    
    def plot(self,):
        print('----------------------------------------')
        print('========== stage plot ==========')
        plt.figure(figsize=(8, 5))
        ax = plt.gca()

        # font 
        content_font = FontProperties(
            fname='/Users/zhoutianze/miniforge3/lib/python3.9/site-packages/matplotlib/mpl-data/fonts/ttf/SimHei.ttf',
            size=13
        )

        title_font = FontProperties(
            fname='/Users/zhoutianze/miniforge3/lib/python3.9/site-packages/matplotlib/mpl-data/fonts/ttf/SimHei.ttf',
            size=15
        )

        for ally_key in self.allies_info:
            print(ally_key)
            ally_data = self.allies_info[ally_key]
            ori_ally_data = ally_data[::self.stage_len]

            ally_data = np.array(ally_data)
            if int(ally_key) <= 2:
                ax.plot(ally_data[::5, 1], ally_data[::5, 2], c='g', linewidth=2)
            else:
                ax.plot(ally_data[::5, 1], ally_data[::5, 2], c='r', linewidth=2)
            
            # arrow
            for ori_data in ori_ally_data:
                ax.arrow(ori_data[1], 
                          ori_data[2], 
                          np.cos(ori_data[3]) * 20, 
                          np.sin(ori_data[3]) * 20, 
                          shape="full",
                          head_width=5.0)
                ax.text(ori_data[1]-20, 
                         ori_data[2]+20, 
                         ori_data[0], 
                         fontsize=8)

        for enemy_key in self.enemies_info:
            enemy_data = self.enemies_info[enemy_key]
            enemy_data = np.array(enemy_data)[::40]
            n_enemy_data = enemy_data.shape[0]

            for i in range(0, n_enemy_data, n_enemy_data-1):
                plt.scatter(enemy_data[i, 1], 
                            enemy_data[i, 2], 
                            c='b', 
                            s=5+15*i/n_enemy_data,
                            alpha=max(0.1, (i/n_enemy_data)**2))
            plt.plot(enemy_data[:, 1], 
                     enemy_data[:, 2], 
                     c='b', 
                     linewidth=0.7,
                     alpha=0.13)

        ax.grid(alpha=0.2, linestyle='--',)
        ax.set_xlim(-50, 850)
        ax.set_ylim(-50, 550)
        ax.invert_yaxis()
        ax.set_title('动态目标场景轨迹图', FontProperties=title_font)
        ax.set_xlabel('x轴坐标', FontProperties=content_font)
        ax.set_ylabel('y轴坐标', FontProperties=content_font)
        plt.show()



class StageGenAttack():
    def __init__(self, stage_len=30):
        self.stage_len = stage_len

        self.allies_info = {}
        self.enemies_info = {}

    def step(self, allies, enemies, step):
        
        # if step % self.stage_len == 0:
        #     return

        for ally in allies:
            # add new ally
            if ally.id not in self.allies_info:
                self.allies_info[ally.id] = []

            if ally.alive:
                if isinstance(ally.ori, np.ndarray):
                    ori = ally.ori[0]
                else:
                    ori = ally.ori
                self.allies_info[ally.id].append(
                    [step, ally.pos[0], ally.pos[1], float(ori)]
                )

        for enemy in enemies:
            # add new enemy
            if enemy.id not in self.enemies_info:
                self.enemies_info[enemy.id] = []
            
            if enemy.alive:
                if isinstance(enemy.ori, np.ndarray):
                    ori = enemy.ori[0]
                else:
                    ori = enemy.ori
                self.enemies_info[enemy.id].append(
                    [step, enemy.pos[0], enemy.pos[1], float(ori)]
                )
    
    def plot(self,):
        print('----------------------------------------')
        print('========== stage plot ==========')
        plt.figure(figsize=(8, 5))
        ax = plt.gca()

        # font 
        content_font = FontProperties(
            fname='/Users/zhoutianze/miniforge3/lib/python3.9/site-packages/matplotlib/mpl-data/fonts/ttf/SimHei.ttf',
            size=13
        )

        title_font = FontProperties(
            fname='/Users/zhoutianze/miniforge3/lib/python3.9/site-packages/matplotlib/mpl-data/fonts/ttf/SimHei.ttf',
            size=15
        )

        for ally_key in self.allies_info:
            ally_data = self.allies_info[ally_key]
            ori_ally_data = ally_data[::self.stage_len]

            ally_data = np.array(ally_data)
            ax.plot(ally_data[::5, 1], ally_data[::5, 2], c='r', linewidth=2)
            
            # arrow
            for ori_data in ori_ally_data:
                ax.arrow(ori_data[1], 
                          ori_data[2], 
                          np.cos(ori_data[3]) * 20, 
                          np.sin(ori_data[3]) * 20, 
                          shape="full",
                          head_width=5.0)
                ax.text(ori_data[1]-10, 
                         ori_data[2]+10, 
                         ori_data[0], 
                         fontsize=6)

        for enemy_key in self.enemies_info:
            enemy_data = self.enemies_info[enemy_key]
            enemy_data = np.array(enemy_data)[::30]
            n_enemy_data = enemy_data.shape[0]

            for i in range(0, n_enemy_data, n_enemy_data-1):
                ax.scatter(enemy_data[i, 1], 
                            enemy_data[i, 2], 
                            c='b', 
                            s=5+15*i/n_enemy_data,
                            alpha=max(0.1, (i/n_enemy_data)**2))
                ax.text(enemy_data[i, 1]-10, 
                        enemy_data[i, 2]+10,
                        enemy_data[i, 0], 
                        fontsize=6)
            plt.plot(enemy_data[:, 1], 
                     enemy_data[:, 2], 
                     c='b', 
                     linewidth=0.7,
                     alpha=0.13)

        ax.grid(alpha=0.2, linestyle='--',)
        ax.set_xlim(-50, 850)
        ax.set_ylim(-50, 550)
        ax.invert_yaxis()
        ax.set_title('静态目标场景轨迹图', FontProperties=title_font)
        ax.set_xlabel('x轴坐标', FontProperties=content_font)
        ax.set_ylabel('y轴坐标', FontProperties=content_font)
        plt.show()         



        