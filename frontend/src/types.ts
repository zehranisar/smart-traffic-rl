export interface Frame {
  t: number
  queues: number[] // N, S, E, W
  phase: number // 0 = NS green, 1 = EW green
  yellow: boolean
  passed: number
}

export interface Episode {
  frames: Frame[]
  avg_queue: number
  passed: number
}
