import {Flow, Profile, OldTransaction, Report} from '@/models/type'

const profile: Profile = {
  name: '安野貴博',
  title: 'AIエンジニア',
  party: '無所属',
  image: '/demo-takahiroanno.jpg',
}

const reports: Report[] = [
  {
    id: 'demo-takahiro-anno-2024',
    totalIncome: 18416736,
    totalExpense: 7580065,
    totalBalance: 10836671,
    year: 2024,
    orgType: '政治資金規正法第18条の２第１項の規定による政治団体\nその他の政治団体',
    orgName: 'デジタル民主主義を考える会',
    activityArea: '東京都内',
    representative: '安野 貴博',
    fundManagementOrg: '有り/東京都知事候補 安野貴博',
    accountingManager: '安野 貴博',
    administrativeManager: '高山 聡史',
    lastUpdate: '2024年3月31日',
  }
]

const report = reports[0]

const flows: Flow[] = [
  // 収入
  { id: 'i3', name: '個人からの寄附', direction: 'income', value: 16416736, parent: '総収入' },
  { id: 'i8', name: '借入金', direction: 'income', value: 2000000, parent: '総収入' },
  { id: 'i_total', name: '総収入', direction: 'expense', value: 18416736, parent: null },

  // 支出
  { id: 'e4', name: '事務所費', direction: 'expense', value: 1173737, parent: '経常経費' },
  { id: 'e5', name: '経常経費', direction: 'expense', value: 1173737, parent: '総収入' },
  { id: 'e7', name: '選挙関係費', direction: 'expense', value: 2500000, parent: '政治活動費' },
  { id: 'e12', name: '宣伝事業費', direction: 'expense', value: 1906328, parent: '政治活動費' },
  { id: 'e15', name: 'その他の経費', direction: 'expense', value: 2000000, parent: '政治活動費' },
  { id: 'e16', name: '政治活動費', direction: 'expense', value: 6406328, parent: '総収入' },
  // 翌年への繰越
  { id: 'e_next', name: '翌年への繰越額', direction: 'expense', value: 10836671, parent: '総収入' },
]

const incomeTransactions: OldTransaction[] = [
  {
    id: '4-1',
    name: '安野貴博',
    date: '-',
    category: '借入金',
    value: 2000000,
    percentage: 11,
  },
  {
    id: '7-1',
    name: '個人からの寄附',
    date: '-',
    category: '個人からの寄附',
    value: 16416736,
    percentage: 89,
  },
]

const expenseTransactions: OldTransaction[] = [
  {
    id: '14-1',
    name: 'コミュニケーションツール費用(slack)',
    date: '-',
    category: '経常経費',
    value: 107265+152845+80552+63525+62818+66105,
    percentage: 7,
  },
  {
    id: '14-2',
    name: '献金システム手数料(ボネクタ)',
    date: '-',
    category: '経常経費',
    value: 300575+130680,
    percentage: 6,
  },
  {
    id: '14-3',
    name: 'その他の経常経費',
    date: '-',
    category: '経常経費',
    value: 209372,
    percentage: 3,
  },
  {
    id: '15-1',
    name: '寄付',
    date: '-',
    category: '選挙関係費',
    value: 2500000,
    percentage: 33,
  },
  {
    id: '15-2',
    name: 'ブロードリスニングAPI利用料(X)',
    date: '-',
    category: '組織活動費',
    value: 801378,
    percentage: 11,
  },
  {
    id: '15-3',
    name: 'ブロードリスニングAPI利用料(OpenAI)',
    date: '-',
    category: '組織活動費',
    value: 163808+166257+166257,
    percentage: 7,
  },
  {
    id: '15-4',
    name: '政策広報用音声コンテンツ作成API利用料(ElevenLabs)',
    date: '-',
    category: '組織活動費',
    value: 53832+112135+110797+110267+110389+67069,
    percentage: 7,
  },
  {
    id: '15-5',
    name: 'その他の組織活動費',
    date: '-',
    category: '組織活動費',
    value: 44139,
    percentage: 1,
  },
  {
    id: '15-6',
    name: '借入金の返済',
    date: '-',
    category: 'その他の経費',
    value: 2000000,
    percentage: 26,
  },
]

export default {
  id: report.id,
  profile,
  report,
  reports,
  flows,
  incomeTransactions,
  expenseTransactions,
}
