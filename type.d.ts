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

export type Metadata = {
  source: string
  orgType: string
  orgName: string
  activityArea: string
  representative: string
  fundManagementOrg: string
  accountingManager: string
  administrativeManager: string
  lastUpdate: string
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
