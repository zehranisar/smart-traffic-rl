"""Single 4-way intersection as a Gymnasium environment.

Lanes: 0=N, 1=S, 2=E, 3=W.  Phase NS = lanes 0,1 green; phase EW = lanes 2,3 green.
Action = which phase should be green for the next `step_seconds` seconds.
Switching phase costs `yellow_seconds` of lost time (nobody passes).
"""
import numpy as np
import gymnasium as gym
from gymnasium import spaces

NS, EW = 0, 1
GREEN_LANES = {NS: (0, 1), EW: (2, 3)}
ARRIVAL_RATE = {"low": 0.08, "normal": 0.14, "rush": 0.20}  # cars/sec/lane


class TrafficEnv(gym.Env):
    def __init__(self, level="normal", episode_seconds=3600, step_seconds=5,
                 yellow_seconds=3, max_queue=60, saturation=0.5,
                 randomize_flow=True, switch_penalty=0.3, shift_demand=True):
        super().__init__()
        self.level = level
        self.episode_seconds = episode_seconds
        self.step_seconds = step_seconds
        self.yellow_seconds = yellow_seconds
        self.max_queue = max_queue
        self.saturation = saturation          # cars/sec that can leave a green lane
        self.randomize_flow = randomize_flow  # each lane gets a random demand factor
        self.switch_penalty = switch_penalty  # reward cost of changing phase
        self.shift_demand = shift_demand      # heavy direction changes during the episode
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(0.0, 1.0, shape=(7,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        level = (options or {}).get("level", self.level)
        factor = (self.np_random.uniform(0.6, 1.4, size=4)
                  if self.randomize_flow else np.ones(4))
        self.base_rates = ARRIVAL_RATE[level] * factor
        self.rates = self.base_rates.copy()
        # which direction is heavy first; it swaps halfway through the episode
        self.heavy_first = int(self.np_random.integers(2))
        # separate RNG for arrivals: same seed -> same traffic for every policy
        self._arr_rng = np.random.default_rng(int(self.np_random.integers(1 << 31)))
        self.queues = np.zeros(4, dtype=np.int64)
        self.credit = np.zeros(4)
        self.phase, self.time_in_phase, self.yellow_left = NS, 0, 0
        self.t, self.total_wait, self.total_passed = 0, 0, 0
        return self._obs(), {}

    def _current_rates(self):
        if not self.shift_demand:
            return self.base_rates
        first_half = self.t < self.episode_seconds / 2
        heavy_ns = (self.heavy_first == 0) == first_half   # True -> NS is the busy direction
        mult = np.array([1.4, 1.4, 0.6, 0.6]) if heavy_ns else np.array([0.6, 0.6, 1.4, 1.4])
        return self.base_rates * mult

    def _obs(self):
        q = np.minimum(self.queues, self.max_queue) / self.max_queue
        phase = np.eye(2)[self.phase]
        t = min(self.time_in_phase, 60) / 60
        return np.concatenate([q, phase, [t]]).astype(np.float32)

    def _discharge(self):
        passed = 0
        for lane in GREEN_LANES[self.phase]:
            self.credit[lane] += self.saturation
            n = min(int(self.credit[lane]), int(self.queues[lane]))
            self.queues[lane] -= n
            self.credit[lane] -= n
            if self.queues[lane] == 0:
                self.credit[lane] = min(self.credit[lane], 1.0)
            passed += n
        return passed

    def step(self, action):
        action = int(action)
        switched = action != self.phase
        if switched:                      # switching = yellow time lost
            self.phase, self.time_in_phase = action, 0
            self.yellow_left = self.yellow_seconds
            self.credit[:] = 0
        wait = passed = 0
        for _ in range(self.step_seconds):
            self.rates = self._current_rates()
            arrivals = self._arr_rng.random(4) < self.rates
            self.queues = np.minimum(self.queues + arrivals, self.max_queue)
            if self.yellow_left > 0:
                self.yellow_left -= 1
            else:
                passed += self._discharge()
            wait += int(self.queues.sum())            # vehicle-seconds spent waiting
            self.t += 1
        self.time_in_phase += self.step_seconds
        self.total_wait += wait
        self.total_passed += passed
        reward = -wait / 100.0 - (self.switch_penalty if switched else 0.0)
        truncated = self.t >= self.episode_seconds
        info = {"avg_queue": self.total_wait / self.t, "passed": self.total_passed}
        return self._obs(), reward, False, truncated, info
