export type Summary = {
  name: string
  title: string
  support: string
  party: string
  district: string
  image: string
  income: number
  expense: number
  balance: number
  year: number
}

export type Flow = {
  id: string
  direction: 'income'|'expense'
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
