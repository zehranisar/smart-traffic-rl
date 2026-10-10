interface Props {
  fixed: number[]
  rl: number[]
  cursor: number
  baselineLabel: string
  rlLabel: string
}

const W = 640
const H = 200
const PAD = 8

export default function Chart({ fixed, rl, cursor, baselineLabel, rlLabel }: Props) {
  const len = Math.max(fixed.length, rl.length, 2)
  const max = Math.max(1, ...fixed, ...rl)
  const x = (i: number) => PAD + (i / (len - 1)) * (W - 2 * PAD)
  const y = (v: number) => H - PAD - (v / max) * (H - 2 * PAD)
  const line = (data: number[]) => data.map((v, i) => `${x(i)},${y(v)}`).join(' ')

  return (
    <div className="rounded-2xl bg-white p-4 shadow">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="font-semibold text-slate-800">Total waiting cars over time</h3>
        <div className="flex gap-4 text-sm">
          <span className="text-slate-500">● {baselineLabel}</span>
          <span className="text-green-600">● {rlLabel}</span>
        </div>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full">
        <rect width={W} height={H} fill="#f8fafc" rx="8" />
        <polyline points={line(fixed)} fill="none" stroke="#64748b" strokeWidth="2" />
        <polyline points={line(rl)} fill="none" stroke="#16a34a" strokeWidth="2" />
        <line x1={x(cursor)} y1="0" x2={x(cursor)} y2={H} stroke="#0f172a" strokeWidth="1" strokeDasharray="4 4" />
      </svg>
    </div>
  )
}
