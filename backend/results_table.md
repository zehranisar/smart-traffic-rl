Average queue length (cars), mean ± std over 30 unseen traffic scenarios. Lower is better.

| Traffic | Policy | Avg queue | Cars passed |
|---|---|---|---|
| low | Random | 7.7 ± 4.7 | 1108 |
| low | Fixed timer (30s) | 3.9 ± 0.6 | 1114 |
| low | Fixed timer (45s) | 5.3 ± 0.8 | 1111 |
| low | Longest queue | 1.9 ± 0.3 | 1117 |
| low | Q-learning (RL) | 2.4 ± 0.3 | 1117 |
| low | DQN (RL) | 2.1 ± 0.2 | 1117 |
| low | PPO (RL) | 4.3 ± 0.2 | 1115 |
| normal | Random | 59.4 ± 21.9 | 1764 |
| normal | Fixed timer (30s) | 25.2 ± 15.7 | 1912 |
| normal | Fixed timer (45s) | 21.3 ± 11.3 | 1929 |
| normal | Longest queue | 8.0 ± 6.9 | 1962 |
| normal | Q-learning (RL) | 5.6 ± 1.6 | 1964 |
| normal | DQN (RL) | 5.1 ± 1.3 | 1964 |
| normal | PPO (RL) | 6.6 ± 1.0 | 1962 |
| rush | Random | 115.8 ± 17.8 | 2121 |
| rush | Fixed timer (30s) | 75.6 ± 20.2 | 2423 |
| rush | Fixed timer (45s) | 67.6 ± 21.0 | 2493 |
| rush | Longest queue | 95.0 ± 45.9 | 2488 |
| rush | Q-learning (RL) | 42.5 ± 31.5 | 2549 |
| rush | DQN (RL) | 31.9 ± 22.8 | 2730 |
| rush | PPO (RL) | 44.8 ± 38.6 | 2704 |

Reduction in average queue for each RL method (positive = RL is better):

| Traffic | RL method | vs Fixed 30s | vs Fixed 45s | vs Longest queue |
|---|---|---|---|---|
| low | Q-learning (RL) | +37% | +54% | -30% |
| low | DQN (RL) | +45% | +60% | -13% |
| low | PPO (RL) | -11% | +18% | -130% |
| normal | Q-learning (RL) | +78% | +74% | +31% |
| normal | DQN (RL) | +80% | +76% | +37% |
| normal | PPO (RL) | +74% | +69% | +18% |
| rush | Q-learning (RL) | +44% | +37% | +55% |
| rush | DQN (RL) | +58% | +53% | +66% |
| rush | PPO (RL) | +41% | +34% | +53% |
