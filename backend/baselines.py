"""Baseline signal controllers + a shared evaluation function."""
import numpy as np
from env import TrafficEnv, NS, EW


class FixedTimer:
    """Switch phase every `green` seconds, ignoring traffic."""
    name = "Fixed timer"

    def __init__(self, green=30):
        self.green = green

    def act(self, env):
        return (env.t // self.green) % 2


class RandomPolicy:
    name = "Random"

    def __init__(self, seed=0):
        self.rng = np.random.default_rng(seed)

    def act(self, env):
        return int(self.rng.integers(2))


class LongestQueue:
    """Give green to the busier direction (with a minimum green time)."""
    name = "Longest queue"

    def __init__(self, min_green=10):
        self.min_green = min_green

    def act(self, env):
        if env.time_in_phase < self.min_green:
            return env.phase
        ns, ew = env.queues[:2].sum(), env.queues[2:].sum()
        if ns == ew:
            return env.phase
        return NS if ns > ew else EW


def evaluate(policy, level, episodes=10):
    """Return (mean avg queue length, mean cars passed) over fixed test seeds."""
    env = TrafficEnv(level=level)
    queues, passed = [], []
    for ep in range(episodes):
        env.reset(seed=1000 + ep)
        done = False
        while not done:
            _, _, _, done, info = env.step(policy.act(env))
        queues.append(info["avg_queue"])
        passed.append(info["passed"])
    return float(np.mean(queues)), float(np.mean(passed))
