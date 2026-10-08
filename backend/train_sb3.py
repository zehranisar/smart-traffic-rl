"""Train DQN or PPO (Stable-Baselines3) on the traffic environment.

Run:  python train_sb3.py dqn          (or: python train_sb3.py ppo)
Optional: python train_sb3.py dqn 300000   (number of training steps)
Saves: dqn_model.zip / ppo_model.zip
"""
import sys
import numpy as np
from stable_baselines3 import DQN, PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.env_util import make_vec_env

from env import TrafficEnv, ARRIVAL_RATE


class RandomLevelEnv(TrafficEnv):
    """Each training episode uses a random traffic level (low / normal / rush)."""

    def reset(self, seed=None, options=None):
        level = str(np.random.choice(list(ARRIVAL_RATE)))
        return super().reset(seed=seed, options={"level": level})


class SB3Policy:
    """Wraps a trained SB3 model so it can be used like the other controllers."""

    def __init__(self, model, name):
        self.model, self.name = model, name

    def act(self, env):
        action, _ = self.model.predict(env._obs(), deterministic=True)
        return int(action)


class Progress(BaseCallback):
    def __init__(self, every=20_000):
        super().__init__()
        self.every, self.rewards = every, []

    def _on_step(self):
        for info in self.locals.get("infos", []):
            if "episode" in info:
                self.rewards.append(info["episode"]["r"])
        if self.num_timesteps % self.every == 0 and self.rewards:
            print(f"steps {self.num_timesteps:8d}  mean episode reward (last 10) = {np.mean(self.rewards[-10:]):.1f}")
        return True


def load_policy(algo):
    cls = {"dqn": DQN, "ppo": PPO}[algo]
    return SB3Policy(cls.load(f"{algo}_model", device="cpu"), "DQN" if algo == "dqn" else "PPO")


if __name__ == "__main__":
    algo = sys.argv[1].lower() if len(sys.argv) > 1 else "dqn"
    steps = int(sys.argv[2]) if len(sys.argv) > 2 else 300_000
    if algo == "dqn":
        env = Monitor(RandomLevelEnv())
        model = DQN("MlpPolicy", env, learning_rate=5e-4, buffer_size=100_000,
                    learning_starts=5_000, batch_size=128, gamma=0.95,
                    train_freq=4, target_update_interval=2_000,
                    exploration_fraction=0.4, exploration_final_eps=0.05,
                    policy_kwargs=dict(net_arch=[64, 64]), device="cpu", seed=0, verbose=0)
    elif algo == "ppo":
        env = make_vec_env(lambda: Monitor(RandomLevelEnv()), n_envs=4, seed=0)
        model = PPO("MlpPolicy", env, learning_rate=3e-4, n_steps=1440, batch_size=360,
                    gamma=0.95, ent_coef=0.01, policy_kwargs=dict(net_arch=[64, 64]),
                    device="cpu", seed=0, verbose=0)
    else:
        raise SystemExit("use: python train_sb3.py dqn   or   python train_sb3.py ppo")
    print(f"Training {algo.upper()} for {steps} steps ...")
    model.learn(total_timesteps=steps, callback=Progress())
    model.save(f"{algo}_model")
    print(f"saved {algo}_model.zip")
