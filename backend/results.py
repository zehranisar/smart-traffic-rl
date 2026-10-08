"""Fair multi-seed comparison of all controllers. Needs q_table.npy (run train_q.py first).

Run:  python results.py
Creates: results.csv, results_table.md, results_chart.png
"""
import csv
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from env import TrafficEnv, ARRIVAL_RATE
from baselines import RandomPolicy, FixedTimer, LongestQueue
from train_q import QAgent

N_SEEDS = 30
SEEDS = range(5000, 5000 + N_SEEDS)   # never used in training (training uses 10000+)

agent = QAgent()
agent.q = np.load("q_table.npy")
POLICIES = [RandomPolicy(), FixedTimer(30), FixedTimer(45), LongestQueue(10), agent]
NAMES = ["Random", "Fixed timer (30s)", "Fixed timer (45s)", "Longest queue", "Q-learning (RL)"]
COLORS = ["#cbd5e1", "#64748b", "#94a3b8", "#f59e0b", "#16a34a"]

# DQN / PPO are optional: used only if you trained them (python train_sb3.py dqn / ppo)
for algo, label, color in [("dqn", "DQN (RL)", "#2563eb"), ("ppo", "PPO (RL)", "#9333ea")]:
    if os.path.exists(f"{algo}_model.zip"):
        from train_sb3 import load_policy
        POLICIES.append(load_policy(algo)); NAMES.append(label); COLORS.append(color)
RL_NAMES = [n for n in NAMES if "(RL)" in n]


def run(policy, level, seed):
    env = TrafficEnv(level=level)
    env.reset(seed=seed)
    done = False
    while not done:
        _, _, _, done, info = env.step(policy.act(env))
    return info["avg_queue"], info["passed"]


rows = []
for level in ARRIVAL_RATE:
    for name, pol in zip(NAMES, POLICIES):
        res = np.array([run(pol, level, s) for s in SEEDS])
        rows.append({
            "traffic": level, "policy": name,
            "avg_queue_mean": res[:, 0].mean(), "avg_queue_std": res[:, 0].std(),
            "cars_passed_mean": res[:, 1].mean(),
        })

with open("results.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)

# Markdown table + improvement of RL over the best baseline
lines = [f"Average queue length (cars), mean ± std over {N_SEEDS} unseen traffic scenarios. Lower is better.\n",
         "| Traffic | Policy | Avg queue | Cars passed |", "|---|---|---|---|"]
for r in rows:
    lines.append(f"| {r['traffic']} | {r['policy']} | {r['avg_queue_mean']:.1f} ± {r['avg_queue_std']:.1f} | {r['cars_passed_mean']:.0f} |")
lines.append("\nReduction in average queue for each RL method (positive = RL is better):\n")
lines.append("| Traffic | RL method | vs Fixed 30s | vs Fixed 45s | vs Longest queue |")
lines.append("|---|---|---|---|---|")
for level in ARRIVAL_RATE:
    g = {r["policy"]: r["avg_queue_mean"] for r in rows if r["traffic"] == level}
    for rl_name in RL_NAMES:
        imp = lambda b: f"{(g[b] - g[rl_name]) / g[b] * 100:+.0f}%"
        lines.append(f"| {level} | {rl_name} | {imp('Fixed timer (30s)')} | {imp('Fixed timer (45s)')} | {imp('Longest queue')} |")
open("results_table.md", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))

# Grouped bar chart
fig, ax = plt.subplots(figsize=(10, 5))
levels = list(ARRIVAL_RATE)
width = 0.8 / len(NAMES)
colors = COLORS
for i, name in enumerate(NAMES):
    vals = [next(r for r in rows if r["traffic"] == l and r["policy"] == name) for l in levels]
    ax.bar(np.arange(len(levels)) + i * width, [v["avg_queue_mean"] for v in vals], width,
           yerr=[v["avg_queue_std"] for v in vals], capsize=2, label=name, color=colors[i])
ax.set_xticks(np.arange(len(levels)) + width * (len(NAMES) - 1) / 2)
ax.set_xticklabels([l.capitalize() for l in levels])
ax.set_ylabel("Average queue length (cars)")
ax.set_title(f"Controller comparison ({N_SEEDS} unseen scenarios per traffic level)")
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("results_chart.png", dpi=150)
