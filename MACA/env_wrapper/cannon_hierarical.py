
import numpy as np
import networkx as nx

from MACA.env_wrapper.cannon_reconn_hierarical import CannonReconnHieraricalWrapper


class CannonHieraricalAdjWrapper(CannonReconnHieraricalWrapper):
    def __init__(self, args, env):
        super(CannonHieraricalAdjWrapper, self).__init__(args, env)
    
    def obs_wrapper(self, env):
        obses = {}

        adj = self._gen_adj(env)

        for i, ally in enumerate(env.allies):
            obses[str(i+1)] = np.concatenate([self._obs_fighter_wrapper(env, ally), adj], axis=-1)
        return obses

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



        