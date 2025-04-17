import {Flow, Metadata, Profile, Summary, Support, Transaction} from '@/type'

export const profile: Profile = {
  name: '政治 太郎',
  title: '衆議院議員',
  support: '政治資金太郎をみまもる会',
  party: '政治資金党',
  district: '東京1区',
  image: 'https://i.pravatar.cc/300?u=2',
}

export const supports: Support[] = [
  {
    id: 'example',
    name: '政治資金太郎をみまもる会',
  }
]

export const summary: Summary = {
  income: 141180683,
  expense: 13262929,
  balance: 127434080,
  year: 2024,
}

export const metadata: Metadata = {
  source: '2024年政治資金収支報告書',
  orgType: 'その他の政治団体',
  orgName: '政治太郎講演会',
  activityArea: '２以上の都道府県の区域など',
  representative: '政治太郎',
  fundManagementOrg: '有り/衆議院議員(現職)政治太郎',
  accountingManager: '中村太郎',
  administrativeManager: '佐藤太郎',
  lastUpdate: '2024年3月31日',
}

export const flows: Flow[] = [
  // 収入
  {id: 'xxx1', name: '個人からの寄付', direction: 'income', value: 1560000, parent: '寄付'},
  {id: 'xxx2', name: '政治団体からの寄付', direction: 'income', value: 100000, parent: '寄付'},
  {id: 'xxx3', name: '寄付', direction: 'income', value: 1660000, parent: '総収入'},
  {id: 'xxx4', name: '機関紙誌の発行その他の事業による収入', direction: 'income', value: 29910000, parent: '総収入'},
  {id: 'xxx5', name: '前年度からの繰越', direction: 'income', value: 109597655, parent: '総収入'},
  // 総収入
  {id: 'xxx66', name: '総収入', direction: 'expense', value: 141180683, parent: null},
  // 支出
  {id: 'xxx7', name: '経常経費', direction: 'expense', value: 483674, parent: '総収入'},
  {id: 'xxx8', name: '人件費', direction: 'expense', value: 57800, parent: '経常経費'},
  {id: 'xxx9', name: '備品・消耗品費', direction: 'expense', value: 319314, parent: '経常経費'},
  {id: 'xxxa', name: '事務所費', direction: 'expense', value: 106560, parent: '経常経費'},
  {id: 'xxxb', name: '政治活動費', direction: 'expense', value: 13262929, parent: '総収入'},
  {id: 'xxxc', name: '組織活動費', direction: 'expense', value: 4473026, parent: '政治活動費'},
  {id: 'xxxd', name: '機関紙の発行その他の事業費', direction: 'expense', value: 8751150, parent: '政治活動費'},
  {id: 'xxxe', name: '政治資金パーティー開催事業費', direction: 'expense', value: 8751150, parent: '機関紙の発行その他の事業費'},
  {id: 'xxxf', name: '調査研究費', direction: 'expense', value: 28753, parent: '政治活動費'},
  {id: 'xxxg', name: '寄付・交付金', direction: 'expense', value: 10000, parent: '政治活動費'},
  {id: 'xxxh', name: '翌年への繰越', direction: 'expense', value: 127434080, parent: '総収入'},
]

export const incomeTransactions: Transaction[] = [
  {
    id: 'xxx1',
    name: 'AAAAA',
    date: '2024/12/31',
    category: '前年繰越',
    value: 109597655,
    percentage: 72,
  },
  {
    id: 'xxx2',
    name: 'BBBBB',
    date: '2024/12/31',
    category: '事業収入',
    value: 29440000,
    percentage: 20,
  },
  {
    id: 'xxx3',
    name: 'CCCCC',
    date: '2024/12/31',
    category: '個人寄付',
    value: 1000000,
    percentage: 2,
  },
  {
    id: 'xxx4',
    name: 'DDDDD',
    date: '2024/12/31',
    category: '個人寄付',
    value: 500000,
    percentage: 2,
  },
  {
    id: 'xxx5',
    name: 'EEEEE',
    date: '2024/12/31',
    category: '事業収入',
    value: 470000,
    percentage: 2,
  },
  {
    id: 'xxx6',
    name: 'FFFFF',
    date: '2024/12/31',
    category: '事業収入',
    value: 100000,
    percentage: 1,
  },
]

export const expenseTransactions: Transaction[] = [
  {
    id: 'xxx1',
    name: 'AAAAA',
    date: '2024/12/31',
    category: '前年繰越',
    value: 109597655,
    percentage: 72,
  },
  {
    id: 'xxx2',
    name: 'BBBBB',
    date: '2024/12/31',
    category: '事業収入',
    value: 29440000,
    percentage: 20,
  },
  {
    id: 'xxx3',
    name: 'CCCCC',
    date: '2024/12/31',
    category: '個人寄付',
    value: 1000000,
    percentage: 2,
  },
  {
    id: 'xxx4',
    name: 'DDDDD',
    date: '2024/12/31',
    category: '個人寄付',
    value: 500000,
    percentage: 2,
  },
  {
    id: 'xxx5',
    name: 'EEEEE',
    date: '2024/12/31',
    category: '事業収入',
    value: 470000,
    percentage: 2,
  },
  {
    id: 'xxx6',
    name: 'FFFFF',
    date: '2024/12/31',
    category: '事業収入',
    value: 100000,
    percentage: 1,
  },
]

export default {
  id: 'example',
  profile,
  supports,
  summary,
  metadata,
  flows,
  incomeTransactions,
  expenseTransactions,
}
