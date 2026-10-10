import { useEffect, useMemo, useState } from 'react'
import Intersection from './Intersection'
import Chart from './Chart'
import type { Episode } from './types'

const API = 'http://localhost:8000'
const LEVELS = ['low', 'normal', 'rush'] as const
type Level = (typeof LEVELS)[number]
const BASELINES = {
  fixed: 'Fixed timer (30s)',
  longest: 'Longest queue first',
} as const
type Baseline = keyof typeof BASELINES
const RL_ALGOS = {
  rl: 'Q-learning',
  dqn: 'DQN',
  ppo: 'PPO',
} as const
type RlAlgo = keyof typeof RL_ALGOS

async function load(controller: string, level: Level, seed: number): Promise<Episode> {
  const res = await fetch(`${API}/simulate?level=${level}&seed=${seed}&controller=${controller}`)
  if (!res.ok) throw new Error(`API error ${res.status}`)
  return res.json()
}

const sum = (a: number[]) => a.reduce((x, y) => x + y, 0)

function fmtTime(t: number) {
  const m = Math.floor(t / 60)
  const s = t % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

export default function App() {
  const [level, setLevel] = useState<Level>('normal')
  const [baseline, setBaseline] = useState<Baseline>('fixed')
  const [algo, setAlgo] = useState<RlAlgo>('rl')
  const [available, setAvailable] = useState<string[]>(['rl'])
  const [seed, setSeed] = useState(1)
  const [fixed, setFixed] = useState<Episode | null>(null)
  const [rl, setRl] = useState<Episode | null>(null)
  const [idx, setIdx] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [speed, setSpeed] = useState(1)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/controllers`)
      .then((r) => r.json())
      .then((list: string[]) => setAvailable(list))
      .catch(() => {})
  }, [])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    setPlaying(false)
    setIdx(0)
    Promise.all([load(baseline, level, seed), load(algo, level, seed)])
      .then(([f, r]) => {
        if (cancelled) return
        setFixed(f)
        setRl(r)
        setLoading(false)
        setPlaying(true)
      })
      .catch(() => {
        if (cancelled) return
        setError('Backend se connect nahi ho paya. Check karein ke uvicorn chal raha hai (port 8000).')
        setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [level, seed, baseline, algo])

  const last = fixed ? fixed.frames.length - 1 : 0

  useEffect(() => {
    if (!playing || !fixed) return
    const id = setInterval(() => setIdx((i) => Math.min(i + 1, last)), 120 / speed)
    return () => clearInterval(id)
  }, [playing, speed, fixed, last])

  useEffect(() => {
    if (idx >= last && playing) setPlaying(false)
  }, [idx, last, playing])

  const fixedTotals = useMemo(() => (fixed ? fixed.frames.map((f) => sum(f.queues)) : []), [fixed])
  const rlTotals = useMemo(() => (rl ? rl.frames.map((f) => sum(f.queues)) : []), [rl])

  const improvement =
    fixed && rl && fixed.avg_queue > 0 ? ((fixed.avg_queue - rl.avg_queue) / fixed.avg_queue) * 100 : 0

  function togglePlay() {
    if (idx >= last) setIdx(0)
    setPlaying((p) => !p)
  }

  return (
    <div className="min-h-screen bg-slate-100 p-6">
      <div className="mx-auto max-w-6xl space-y-4">
        <header>
          <h1 className="text-2xl font-bold text-slate-900">Smart Traffic Signal Control</h1>
          <p className="text-slate-600">A classic controller vs a Reinforcement Learning agent: same traffic, same intersection.</p>
        </header>

        <div className="flex flex-wrap items-center gap-3 rounded-2xl bg-white p-4 shadow">
          <div className="flex gap-1">
            {LEVELS.map((l) => (
              <button
                key={l}
                onClick={() => setLevel(l)}
                className={`rounded-lg px-3 py-1.5 text-sm font-medium capitalize ${
                  level === l ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {l}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-1">
            <span className="mr-1 text-sm text-slate-700">Compare RL with</span>
            {(Object.keys(BASELINES) as Baseline[]).map((b) => (
              <button
                key={b}
                onClick={() => setBaseline(b)}
                className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
                  baseline === b ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {BASELINES[b]}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-1">
            <span className="mr-1 text-sm text-slate-700">RL algorithm</span>
            {(Object.keys(RL_ALGOS) as RlAlgo[])
              .filter((a) => available.includes(a))
              .map((a) => (
                <button
                  key={a}
                  onClick={() => setAlgo(a)}
                  className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
                    algo === a ? 'bg-green-700 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  {RL_ALGOS[a]}
                </button>
              ))}
          </div>
          <button
            onClick={() => setSeed(Math.floor(Math.random() * 100000))}
            className="rounded-lg bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-200"
          >
            New traffic
          </button>
          <button
            onClick={togglePlay}
            disabled={loading || !!error}
            className="rounded-lg bg-green-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
          >
            {playing ? 'Pause' : idx >= last ? 'Replay' : 'Play'}
          </button>
          <label className="flex items-center gap-2 text-sm text-slate-700">
            Speed
            <select
              value={speed}
              onChange={(e) => setSpeed(Number(e.target.value))}
              className="rounded-lg border border-slate-300 px-2 py-1"
            >
              <option value={1}>1x</option>
              <option value={2}>2x</option>
              <option value={4}>4x</option>
              <option value={8}>8x</option>
            </select>
          </label>
          <input
            type="range"
            min={0}
            max={last}
            value={idx}
            onChange={(e) => {
              setPlaying(false)
              setIdx(Number(e.target.value))
            }}
            className="min-w-40 flex-1"
          />
          <span className="text-sm tabular-nums text-slate-600">
            {fixed ? fmtTime(fixed.frames[idx].t) : '0:00'}
          </span>
        </div>

        {error && <div className="rounded-xl bg-red-100 p-4 text-red-800">{error}</div>}
        {loading && !error && <div className="text-slate-600">Loading simulation...</div>}

        {fixed && rl && !error && (
          <>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-3">
                <Intersection frame={fixed.frames[idx]} title={BASELINES[baseline]} />
                <Stats
                  waiting={fixedTotals[idx]}
                  passed={fixed.frames[idx].passed}
                  avg={fixed.avg_queue}
                />
              </div>
              <div className="space-y-3">
                <Intersection frame={rl.frames[idx]} title={`RL agent (${RL_ALGOS[algo]})`} />
                <Stats waiting={rlTotals[idx]} passed={rl.frames[idx].passed} avg={rl.avg_queue} />
              </div>
            </div>

            <Chart fixed={fixedTotals} rl={rlTotals} cursor={idx} baselineLabel={BASELINES[baseline]} rlLabel={`RL (${RL_ALGOS[algo]})`} />

            <div className="rounded-2xl bg-white p-4 text-center shadow">
              <span className="text-slate-600">Full-episode result: RL vs {BASELINES[baseline]}, average queue </span>
              <span className={`text-lg font-bold ${improvement >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {improvement >= 0 ? `${improvement.toFixed(1)}% better` : `${Math.abs(improvement).toFixed(1)}% worse`}
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function Stats({ waiting, passed, avg }: { waiting: number; passed: number; avg: number }) {
  return (
    <div className="grid grid-cols-3 gap-2 text-center">
      <div className="rounded-xl bg-white p-3 shadow">
        <div className="text-xl font-bold text-slate-900">{waiting}</div>
        <div className="text-xs text-slate-500">Waiting now</div>
      </div>
      <div className="rounded-xl bg-white p-3 shadow">
        <div className="text-xl font-bold text-slate-900">{passed}</div>
        <div className="text-xs text-slate-500">Cars passed</div>
      </div>
      <div className="rounded-xl bg-white p-3 shadow">
        <div className="text-xl font-bold text-slate-900">{avg.toFixed(1)}</div>
        <div className="text-xs text-slate-500">Avg queue (full run)</div>
      </div>
    </div>
  )
}
