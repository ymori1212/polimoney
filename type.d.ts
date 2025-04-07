export type Summary = {
  name: string
  title: string
  support: string
  party: string
  district: string
  in: number
  out: number
  transfer: number
  year: number
}

export type Flow = {
  id: string
  direction: 'in'|'out'
  value: number
  parent: string | null
}

export type Transaction = {
  id: string
  category: string
  date: string
  value: number
  percentage: number
}
