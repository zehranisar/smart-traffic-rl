"""FastAPI server: runs the simulation and sends frame-by-frame data to the frontend.

Run:  uvicorn api:app --reload --port 8000
"""
import os
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from env import TrafficEnv, ARRIVAL_RATE
from baselines import FixedTimer, LongestQueue
from train_q import QAgent

app = FastAPI(title="Smart Traffic RL")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Q_PATH = os.path.join(os.path.dirname(__file__), "q_table.npy")
agent = QAgent()
if os.path.exists(Q_PATH):
    agent.q = np.load(Q_PATH)

CONTROLLERS = {
    "fixed": FixedTimer(30),
    "longest": LongestQueue(10),
    "rl": agent,
}

# Optional deep-RL controllers (available after: python train_sb3.py dqn / ppo)
for _algo in ("dqn", "ppo"):
    if os.path.exists(os.path.join(os.path.dirname(__file__), f"{_algo}_model.zip")):
        try:
            from train_sb3 import load_policy
            CONTROLLERS[_algo] = load_policy(_algo)
        except Exception as e:  # stable-baselines3 / torch not installed
            print(f"Could not load {_algo}: {e}")


@app.get("/controllers")
def controllers():
    return list(CONTROLLERS)


def run_episode(policy, level, seed):
    env = TrafficEnv(level=level)
    env.reset(seed=seed)
    frames, done = [], False
    while not done:
        _, _, _, done, info = env.step(policy.act(env))
        frames.append({
            "t": env.t,
            "queues": [int(q) for q in env.queues],  # N, S, E, W
            "phase": env.phase,                       # 0 = NS green, 1 = EW green
            "yellow": env.yellow_left > 0,
            "passed": info["passed"],
        })
    return {"frames": frames, "avg_queue": info["avg_queue"], "passed": info["passed"]}


@app.get("/simulate")
def simulate(level: str = "normal", seed: int = 1, controller: str = "rl"):
    if level not in ARRIVAL_RATE:
        raise HTTPException(400, f"level must be one of {list(ARRIVAL_RATE)}")
    if controller not in CONTROLLERS:
        raise HTTPException(400, f"controller must be one of {list(CONTROLLERS)}")
    return run_episode(CONTROLLERS[controller], level, seed)
