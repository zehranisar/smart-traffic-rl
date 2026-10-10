import type { Frame } from './types'

const C = 160
const HALF = 28
const GAP = 13
const MAX_DRAW = 9

function lightColor(frame: Frame, axis: 'ns' | 'ew') {
  if (frame.yellow) return '#f59e0b'
  const green = (axis === 'ns') === (frame.phase === 0)
  return green ? '#22c55e' : '#ef4444'
}

interface Props {
  frame: Frame
  title: string
}

export default function Intersection({ frame, title }: Props) {
  const [n, s, e, w] = frame.queues
  const ns = lightColor(frame, 'ns')
  const ew = lightColor(frame, 'ew')
  const idx = (count: number) =>
    Array.from({ length: Math.min(count, MAX_DRAW) }, (_, i) => i)

  return (
    <div className="rounded-2xl bg-white p-4 shadow">
      <h3 className="mb-2 text-center text-lg font-semibold text-slate-800">{title}</h3>
      <svg viewBox="0 0 320 320" className="mx-auto w-full max-w-sm">
        <rect width="320" height="320" rx="12" fill="#e2e8f0" />
        <rect x={C - HALF} y="0" width={2 * HALF} height="320" fill="#475569" />
        <rect x="0" y={C - HALF} width="320" height={2 * HALF} fill="#475569" />
        <g stroke="#f8fafc" strokeWidth="2" strokeDasharray="6 6">
          <line x1={C} y1="0" x2={C} y2={C - HALF} />
          <line x1={C} y1={C + HALF} x2={C} y2="320" />
          <line x1="0" y1={C} x2={C - HALF} y2={C} />
          <line x1={C + HALF} y1={C} x2="320" y2={C} />
        </g>

        {idx(n).map((i) => (
          <rect key={`n${i}`} x={C - HALF + 6} y={C - HALF - 18 - i * GAP} width="10" height="12" rx="2" fill="#2563eb" />
        ))}
        {idx(s).map((i) => (
          <rect key={`s${i}`} x={C + HALF - 16} y={C + HALF + 6 + i * GAP} width="10" height="12" rx="2" fill="#2563eb" />
        ))}
        {idx(e).map((i) => (
          <rect key={`e${i}`} x={C + HALF + 6 + i * GAP} y={C - HALF + 6} width="12" height="10" rx="2" fill="#ea580c" />
        ))}
        {idx(w).map((i) => (
          <rect key={`w${i}`} x={C - HALF - 18 - i * GAP} y={C + HALF - 16} width="12" height="10" rx="2" fill="#ea580c" />
        ))}

        <g fontSize="13" fontWeight="600" fill="#0f172a">
          <text x={C + HALF + 8} y="22">N: {n}</text>
          <text x={C - HALF - 8} y="312" textAnchor="end">S: {s}</text>
          <text x="312" y={C - HALF - 8} textAnchor="end">E: {e}</text>
          <text x="8" y={C + HALF + 20}>W: {w}</text>
        </g>

        <circle cx={C - HALF - 10} cy={C - HALF - 10} r="7" fill={ns} />
        <circle cx={C + HALF + 10} cy={C + HALF + 10} r="7" fill={ns} />
        <circle cx={C + HALF + 10} cy={C - HALF - 10} r="7" fill={ew} />
        <circle cx={C - HALF - 10} cy={C + HALF + 10} r="7" fill={ew} />
      </svg>
    </div>
  )
}
