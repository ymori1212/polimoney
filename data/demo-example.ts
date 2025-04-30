import {Flow, Metadata, Profile, Summary, Source, Transaction} from '@/models/type'

export const profile: Profile = {
  name: 'テスト太郎',
  title: 'テスト党',
  party: 'テスト党',
  image: '/demo-example.png',
}

export const sources: Source[] = [
  {
    id: 'demo-example',
    name: 'テストの会',
    year: 2023,
  }
]

export const summary: Summary = {
  income: 111111,
  expense: 100000,
  balance: 11111,
}

export const metadata: Metadata = {
  source: '2023年政治資金収支報告書',
  orgType: 'その他の政治団体',
  orgName: 'テストの会',
  activityArea: '2以上の都道府県の区域等',
  representative: 'テスト花子',
  fundManagementOrg: '有/参議院議員(現職)テスト花子',
  accountingManager: 'テスト花子',
  administrativeManager: 'テスト花子',
  lastUpdate: '2024年1月1日',
}

export const flows: Flow[] = [
  // 収入
  {id: 'i11', name: '個人からの寄附', direction: 'income', value: 111111, parent: '総収入'},
  {id: 'i99', name: '総収入', direction: 'expense', value: 111111, parent: null},

  // 支出
  {id: 'e11', name: '経常経費', direction: 'expense', value: 100000, parent: '総収入'},
  {id: 'e13', name: '翌年への繰越額', direction: 'expense', value: 11111, parent: '総収入'},
  {id: 'e21', name: '人件費', direction: 'expense', value: 100000, parent: '経常経費'},
]

export const transactions: Transaction[] = [
  {
    'id': '7-1-1',
    'direction': '収入',
    'category': '寄附',
    'subCategory': '個人',
    'purpose': '',
    'name': '個人からの寄附(111名)',
    'amount': 111111,
    'date': ''
  },
  {
    'id': '14-3-13',
    'direction': '支出',
    'category': '経常経費',
    'subCategory': '人件費',
    'purpose': '人件費',
    'name': '人件費',
    'amount': 100000,
    'date': '2024/1/1'
  }
]

export default {
  id: 'demo-example',
  profile, supports: sources, summary, metadata, flows, transactions,
}
