import {Flow, Metadata, Profile, Summary, Support, Transaction} from '@/type'

export const profile: Profile = {
  name: '出井 良輔',
  title: '自由民主党',
  support: '自由民主党東京都中野区第二十支部',
  party: '自由民主党',
  district: '東京都中野区',
  image: '/demo-ryosukeidei.jpg',
}

export const supports: Support[] = [
  {
    id: '1',
    name: '自由民主党東京都中野区第二十支部',
  }
]

export const summary: Summary = {
  income: 30874279,
  expense: 29974871,
  balance: 899408,
  year: 2024,
}

export const metadata: Metadata = {
  source: '令和6年政治資金収支報告書',
  orgType: '政党の支部',
  orgName: '自由民主党東京都中野区第二十支部',
  activityArea: '東京都内',
  representative: '出井 良輔',
  fundManagementOrg: '無し',
  accountingManager: '栢森 高志',
  administrativeManager: '出井 良輔',
  lastUpdate: '令和7年2月13日',
}

export const flows: Flow[] = [
  // 収入
  { id: 'i1', name: '前年からの繰越額', direction: 'income', value: 3406179, parent: '総収入' },
  { id: 'i2', name: '個人の負担する党費又は会費', direction: 'income', value: 251100, parent: '本年の収入額' },
  { id: 'i3', name: '個人からの寄附', direction: 'income', value: 14627000, parent: '寄附' },
  { id: 'i4', name: '法人その他の団体からの寄附', direction: 'income', value: 6530000, parent: '寄附' },
  { id: 'i5', name: '政治団体からの寄附', direction: 'income', value: 1810000, parent: '寄附' },
  { id: 'i6', name: '寄附', direction: 'income', value: 22967000, parent: '本年の収入額' },
  { id: 'i7', name: '本部又は支部から供与された交付金', direction: 'income', value: 1250000, parent: '本年の収入額' },
  { id: 'i8', name: 'その他の収入', direction: 'income', value: 3000000, parent: '本年の収入額' },
  { id: 'i9', name: '本年の収入額', direction: 'income', value: 27468100, parent: '総収入' },
  // 総収入
  { id: 'i_total', name: '総収入', direction: 'expense', value: 30874279, parent: null },
  // 支出
  { id: 'e1', name: '人件費', direction: 'expense', value: 3600000, parent: '経常経費' },
  { id: 'e2', name: '光熱水費', direction: 'expense', value: 240000, parent: '経常経費' },
  { id: 'e3', name: '備品・消耗品費', direction: 'expense', value: 1858006, parent: '経常経費' },
  { id: 'e4', name: '事務所費', direction: 'expense', value: 9701324, parent: '経常経費' },
  { id: 'e5', name: '経常経費', direction: 'expense', value: 15399330, parent: '総収入' },
  { id: 'e6', name: '組織活動費', direction: 'expense', value: 3623335, parent: '政治活動費' },
  { id: 'e7', name: '選挙関係費', direction: 'expense', value: 4000000, parent: '政治活動費' },
  { id: 'e8', name: '宣伝事業費', direction: 'expense', value: 6852206, parent: '機関紙誌の発行その他の事業費' },
  { id: 'e9', name: '機関紙誌の発行その他の事業費', direction: 'expense', value: 6852206, parent: '政治活動費' },
  // { id: 'e10', name: '調査研究費', direction: 'expense', value: 0, parent: '政治活動費' },
  { id: 'e11', name: '寄附・交付金', direction: 'expense', value: 100000, parent: '政治活動費' },
  // { id: 'e12', name: 'その他の経費', direction: 'expense', value: 0, parent: '政治活動費' },
  { id: 'e13', name: '政治活動費', direction: 'expense', value: 14575541, parent: '総収入' },
  // 翌年への繰越
  { id: 'e_next', name: '翌年への繰越', direction: 'expense', value: 899408, parent: '総収入' },
]

export const incomeTransactions: Transaction[] = [
  {
    id: 'i1',
    name: '前年からの繰越額',
    date: '2024/12/31',
    category: '前年繰越',
    value: 3406179,
    percentage: +(3406179 / 30874279 * 100).toFixed(1),
  },
  {
    id: 'i2',
    name: '個人の負担する党費又は会費',
    date: '2024/12/31',
    category: '党費・会費',
    value: 251100,
    percentage: +(251100 / 30874279 * 100).toFixed(1),
  },
  {
    id: 'i3',
    name: '個人からの寄附',
    date: '2024/12/31',
    category: '寄附',
    value: 14627000,
    percentage: +(14627000 / 30874279 * 100).toFixed(1),
  },
  {
    id: 'i4',
    name: '法人その他の団体からの寄附',
    date: '2024/12/31',
    category: '寄附',
    value: 6530000,
    percentage: +(6530000 / 30874279 * 100).toFixed(1),
  },
  {
    id: 'i5',
    name: '政治団体からの寄附',
    date: '2024/12/31',
    category: '寄附',
    value: 1810000,
    percentage: +(1810000 / 30874279 * 100).toFixed(1),
  },
  {
    id: 'i6',
    name: '本部又は支部から供与された交付金',
    date: '2024/12/31',
    category: '交付金',
    value: 1250000,
    percentage: +(1250000 / 30874279 * 100).toFixed(1),
  },
  {
    id: 'i7',
    name: 'その他の収入',
    date: '2024/12/31',
    category: 'その他収入',
    value: 3000000,
    percentage: +(3000000 / 30874279 * 100).toFixed(1),
  },
]

export const expenseTransactions: Transaction[] = [
  {
    id: 'e1',
    name: '人件費',
    date: '2024/12/31',
    category: '経常経費',
    value: 3600000,
    percentage: +(3600000 / 29974871 * 100).toFixed(1),
  },
  {
    id: 'e2',
    name: '光熱水費',
    date: '2024/12/31',
    category: '経常経費',
    value: 240000,
    percentage: +(240000 / 29974871 * 100).toFixed(1),
  },
  {
    id: 'e3',
    name: '備品・消耗品費',
    date: '2024/12/31',
    category: '経常経費',
    value: 1858006,
    percentage: +(1858006 / 29974871 * 100).toFixed(1),
  },
  {
    id: 'e4',
    name: '事務所費',
    date: '2024/12/31',
    category: '経常経費',
    value: 9701324,
    percentage: +(9701324 / 29974871 * 100).toFixed(1),
  },
  {
    id: 'e5',
    name: '組織活動費',
    date: '2024/12/31',
    category: '政治活動費',
    value: 3623335,
    percentage: +(3623335 / 29974871 * 100).toFixed(1),
  },
  {
    id: 'e6',
    name: '選挙関係費',
    date: '2024/12/31',
    category: '政治活動費',
    value: 4000000,
    percentage: +(4000000 / 29974871 * 100).toFixed(1),
  },
  {
    id: 'e7',
    name: '宣伝事業費',
    date: '2024/12/31',
    category: '機関紙誌の発行その他の事業費',
    value: 6852206,
    percentage: +(6852206 / 29974871 * 100).toFixed(1),
  },
  {
    id: 'e8',
    name: '調査研究費',
    date: '2024/12/31',
    category: '政治活動費',
    value: 0,
    percentage: 0,
  },
  {
    id: 'e9',
    name: '寄附・交付金',
    date: '2024/12/31',
    category: '政治活動費',
    value: 100000,
    percentage: +(100000 / 29974871 * 100).toFixed(1),
  },
  {
    id: 'e10',
    name: 'その他の経費',
    date: '2024/12/31',
    category: '政治活動費',
    value: 0,
    percentage: 0,
  },
]

export default {
  id: 'demo-ryosuke-idei-2024',
  profile, supports, summary, metadata, flows, incomeTransactions, expenseTransactions,
}
