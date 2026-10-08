"""Tabular Q-learning agent for the traffic signal environment.

Run:  python train_q.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from env import TrafficEnv, ARRIVAL_RATE
from baselines import FixedTimer, RandomPolicy, LongestQueue, evaluate

BIN_EDGES = [0, 1, 4, 8, 13, 20, 30, 45]  # queue-size bins -> 8 levels (0..7)
N_Q = len(BIN_EDGES)


def qbin(x):
    return int(np.searchsorted(BIN_EDGES, x, side="right") - 1)


def state_of(env):
    ns = qbin(env.queues[:2].sum())
    ew = qbin(env.queues[2:].sum())
    t = 0 if env.time_in_phase < 10 else 1 if env.time_in_phase < 20 else 2 if env.time_in_phase < 40 else 3
    return ns, ew, env.phase, t


class QAgent:
    name = "Q-learning"

    def __init__(self):
        self.q = np.zeros((N_Q, N_Q, 2, 4, 2))

    def act(self, env):
        return int(np.argmax(self.q[state_of(env)]))


def train(episodes=3000, alpha=0.1, gamma=0.95, eps_end=0.05):
    agent, env = QAgent(), TrafficEnv()
    rng = np.random.default_rng(0)
    levels = list(ARRIVAL_RATE)
    history = []
    for ep in range(episodes):
        eps = max(eps_end, 1 - ep / (0.6 * episodes))
        env.reset(seed=10_000 + ep, options={"level": levels[ep % 3]})
        s, done, total = state_of(env), False, 0.0
        while not done:
            a = int(rng.integers(2)) if rng.random() < eps else int(np.argmax(agent.q[s]))
            _, r, _, done, _ = env.step(a)
            s2 = state_of(env)
            agent.q[s + (a,)] += alpha * (r + gamma * agent.q[s2].max() - agent.q[s + (a,)])
            s, total = s2, total + r
        history.append(total)
        if (ep + 1) % 100 == 0:
            print(f"episode {ep + 1:5d}  eps={eps:.2f}  reward={np.mean(history[-100:]):.1f}")
    return agent, history


if __name__ == "__main__":
    agent, history = train()
    np.save("q_table.npy", agent.q)

    plt.plot(np.convolve(history, np.ones(50) / 50, mode="valid"))
    plt.xlabel("Episode"); plt.ylabel("Reward (50-ep moving avg)")
    plt.title("Q-learning training curve"); plt.savefig("training_curve.png", dpi=150)

    policies = [RandomPolicy(), FixedTimer(30), LongestQueue(10), agent]
    print(f"\n{'Traffic':8s} {'Policy':15s} {'Avg queue':>10s} {'Cars passed':>12s}")
    for level in ARRIVAL_RATE:
        for p in policies:
            q, passed = evaluate(p, level)
            print(f"{level:8s} {p.name:15s} {q:10.2f} {passed:12.0f}")
        print()
