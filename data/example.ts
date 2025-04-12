import {Flow, Metadata, Summary, Transaction} from '@/type'

export const summary: Summary = {
  name: '政治資金太郎',
  title: '衆議院議員',
  support: '政治資金太郎をみまもる会',
  party: '政治資金党',
  district: '東京1区',
  image: 'https://i.pravatar.cc/300?u=2',
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
  {id: '個人からの寄付', direction: 'income', value: 1560000, parent: '寄付'},
  {id: '政治団体からの寄付', direction: 'income', value: 100000, parent: '寄付'},
  {id: '寄付', direction: 'income', value: 1660000, parent: '総収入'},
  {id: '機関紙誌の発行その他の事業による収入', direction: 'income', value: 29910000, parent: '総収入'},
  {id: '前年度からの繰越', direction: 'income', value: 109597655, parent: '総収入'},
  // 総収入
  {id: '総収入', direction: 'expense', value: 141180683, parent: null},
  // 支出
  {id: '経常経費', direction: 'expense', value: 483674, parent: '総収入'},
  {id: '人件費', direction: 'expense', value: 57800, parent: '経常経費'},
  {id: '備品・消耗品費', direction: 'expense', value: 319314, parent: '経常経費'},
  {id: '事務所費', direction: 'expense', value: 106560, parent: '経常経費'},
  {id: '政治活動費', direction: 'expense', value: 13262929, parent: '総収入'},
  {id: '組織活動費', direction: 'expense', value: 4473026, parent: '政治活動費'},
  {id: '機関紙の発行その他の事業費', direction: 'expense', value: 8751150, parent: '政治活動費'},
  {id: '政治資金パーティー開催事業費', direction: 'expense', value: 8751150, parent: '機関紙の発行その他の事業費'},
  {id: '調査研究費', direction: 'expense', value: 28753, parent: '政治活動費'},
  {id: '寄付・交付金', direction: 'expense', value: 10000, parent: '政治活動費'},
  {id: '翌年への繰越', direction: 'expense', value: 127434080, parent: '総収入'},
]

export const inTransactions: Transaction[] = [
  {
    id: 'AAAAA',
    date: '2023.1.1',
    category: '前年繰越',
    value: 109597655,
    percentage: 72,
  },
  {
    id: 'BBBBB',
    date: '2023.10.23',
    category: '事業収入',
    value: 29440000,
    percentage: 20,
  },
  {
    id: 'CCCCC',
    date: '2023.12.11',
    category: '個人寄付',
    value: 1000000,
    percentage: 2,
  },
  {
    id: 'DDDDD',
    date: '2023.12.11',
    category: '個人寄付',
    value: 500000,
    percentage: 2,
  },
  {
    id: 'EEEEE',
    date: '2023.12.11',
    category: '事業収入',
    value: 470000,
    percentage: 2,
  },
  {
    id: 'FFFFF',
    date: '2023.12.11',
    category: '事業収入',
    value: 100000,
    percentage: 1,
  },
]

export const outTransactions: Transaction[] = [
  {
    id: 'AAAAA',
    date: '2023.1.1',
    category: '前年繰越',
    value: 109597655,
    percentage: 72,
  },
  {
    id: 'BBBBB',
    date: '2023.10.23',
    category: '事業収入',
    value: 29440000,
    percentage: 20,
  },
  {
    id: 'CCCCC',
    date: '2023.12.11',
    category: '個人寄付',
    value: 1000000,
    percentage: 2,
  },
  {
    id: 'DDDDD',
    date: '2023.12.11',
    category: '個人寄付',
    value: 500000,
    percentage: 2,
  },
  {
    id: 'EEEEE',
    date: '2023.12.11',
    category: '事業収入',
    value: 470000,
    percentage: 2,
  },
  {
    id: 'FFFFF',
    date: '2023.12.11',
    category: '事業収入',
    value: 100000,
    percentage: 1,
  },
]

//
// 石破茂さんの例
// https://www.soumu.go.jp/senkyo/seiji_s/seijishikin/contents/SS20241129/100430_0030.pdf
//

// export const summary: Summary = {
//   name: '石破 茂',
//   title: '衆議院議員',
//   support: '石破茂後援会連絡会',
//   party: '（記載なし）',
//   district: '鳥取県',
//   image: 'https://i.pravatar.cc/300?u=ishiba',
//   in: 141180683,
//   out: 13746603,
//   transfer: 127434080,
//   year: 2023,
// }
//
// export const flows: Flow[] = [
//   // 収入
//   { id: '個人からの寄付', direction: 'income', value: 1560000, parent: '寄付' },
//   { id: '政治団体からの寄付', direction: 'income', value: 100000, parent: '寄付' },
//   { id: '寄付', direction: 'income', value: 1660000, parent: '本年の収入' },
//   { id: '機関紙誌の発行その他の事業による収入', direction: 'income', value: 29910000, parent: '本年の収入' },
//   { id: 'その他の収入（1件10万円未満）', direction: 'income', value: 13028, parent: '本年の収入' },
//   { id: '本年の収入', direction: 'income', value: 31583028, parent: '総収入' },
//   { id: '前年度からの繰越', direction: 'income', value: 109597655, parent: '総収入' },
//   { id: '総収入', direction: 'expense', value: 141180683, parent: null },
//
//   // 支出
//   { id: '経常経費', direction: 'expense', value: 483674, parent: '総収入' },
//   { id: '人件費', direction: 'expense', value: 57800, parent: '経常経費' },
//   { id: '備品・消耗品費', direction: 'expense', value: 319314, parent: '経常経費' },
//   { id: '事務所費', direction: 'expense', value: 106560, parent: '経常経費' },
//   { id: '政治活動費', direction: 'expense', value: 13262929, parent: '総収入' },
//   { id: '組織活動費', direction: 'expense', value: 4473026, parent: '政治活動費' },
//   { id: '機関紙誌の発行その他の事業費', direction: 'expense', value: 8751150, parent: '政治活動費' },
//   { id: '政治資金パーティー開催事業費', direction: 'expense', value: 8751150, parent: '機関紙誌の発行その他の事業費' },
//   { id: '調査研究費', direction: 'expense', value: 28753, parent: '政治活動費' },
//   { id: '寄付・交付金', direction: 'expense', value: 10000, parent: '政治活動費' },
//   { id: '翌年への繰越', direction: 'expense', value: 127434080, parent: '総収入' },
// ]
//
// export const inTransactions: Transaction[] = [
//   { id: '前年繰越', date: '2023.01.01', category: '前年繰越', value: 109597655, percentage: 78 },
//   { id: '石破茂セミナー2023', date: '2023.10.23', category: '事業収入', value: 29440000, percentage: 21 },
//   { id: '石破茂君を囲む会', date: '2023.11.29', category: '事業収入', value: 470000, percentage: 0 },
//   { id: '後藤憲人', date: '2023.12.11', category: '個人寄付', value: 1000000, percentage: 1 },
//   { id: '林弘明', date: '2023.11.24', category: '個人寄付', value: 500000, percentage: 0 },
//   { id: '北田靖則', date: '2023.07.27', category: '個人寄付', value: 20000, percentage: 0 },
//   { id: '自民党支部山形県第1支部', date: '2023.02.23', category: '政治団体寄付', value: 100000, percentage: 0 },
//   { id: 'その他の収入', date: '2023.12.31', category: 'その他収入', value: 13028, percentage: 0 },
// ]
//
// export const outTransactions: Transaction[] = [
//   { id: '政治資金パーティ飲食費', date: '2023.02.21', category: '政治資金パーティ開催費', value: 2441826, percentage: 18 },
//   { id: '政治資金パーティ会議室費', date: '2023.12.11', category: '政治資金パーティ開催費', value: 3641000, percentage: 26 },
//   { id: '政治資金パーティお土産代', date: '2023.10.16', category: '政治資金パーティ開催費', value: 1036800, percentage: 8 },
//   { id: '会合飲食費', date: '2023.01.17', category: '組織活動費', value: 110775, percentage: 1 },
//   { id: '政治資金パーティ飲食その他', date: '2023.12.08', category: '政治資金パーティ開催費', value: 697192, percentage: 5 },
//   { id: '印刷代', date: '2023.12.08', category: '政治資金パーティ開催費', value: 443300, percentage: 3 },
//   { id: '人件費', date: '2023.12.31', category: '経常経費', value: 57800, percentage: 0 },
//   { id: '備品消耗品費', date: '2023.12.31', category: '経常経費', value: 319314, percentage: 2 },
//   { id: '事務所費', date: '2023.06.23', category: '経常経費', value: 106560, percentage: 1 },
// ]

//
// 榛葉賀津也さんの例
// https://www.pref.shizuoka.jp/_res/projects/default_project/_page_/001/046/661/kn08.pdf
//

// export const summary: Summary = {
//   name: '榛葉 賀津也',
//   title: '参議院議員',
//   support: 'しんば賀津也と歩む会',
//   party: '国民民主党',
//   district: '静岡県',
//   image: 'https://i.pravatar.cc/300?u=shinba',
//   in: 1309686,
//   out: 812764,
//   transfer: 496922,
//   year: 2021,
// }
//
// export const flows: Flow[] = [
//   // 収入
//   { id: '党費又は会費', direction: 'income', value: 440000, parent: '本年の収入' },
//   { id: '政治団体からの寄付', direction: 'income', value: 326000, parent: '寄付' },
//   { id: '寄付', direction: 'income', value: 326000, parent: '本年の収入' },
//   { id: 'その他の収入（10万円未満）', direction: 'income', value: 4, parent: '本年の収入' },
//   { id: '本年の収入', direction: 'income', value: 766004, parent: '総収入' },
//   { id: '前年からの繰越', direction: 'income', value: 543682, parent: '総収入' },
//   { id: '総収入', direction: 'expense', value: 1309686, parent: null },
//
//   // 支出
//   { id: '経常経費', direction: 'expense', value: 53350, parent: '総収入' },
//   { id: '事務所費', direction: 'expense', value: 53350, parent: '経常経費' },
//   { id: '政治活動費', direction: 'expense', value: 759414, parent: '総収入' },
//   { id: '組織活動費', direction: 'expense', value: 101433, parent: '政治活動費' },
//   { id: '機関紙誌の発行その他の事業費', direction: 'expense', value: 657981, parent: '政治活動費' },
//   { id: '翌年への繰越', direction: 'expense', value: 496922, parent: '総収入' },
// ]
//
// export const inTransactions: Transaction[] = [
//   { id: '前年繰越', date: '2021.01.01', category: '前年繰越', value: 543682, percentage: 42 },
//   { id: '党費又は会費', date: '2021.12.31', category: '会費', value: 440000, percentage: 34 },
//   { id: '国民民主党静岡県第2総支部', date: '2021.09.28', category: '政治団体寄付', value: 326000, percentage: 25 },
//   { id: 'その他収入', date: '2021.12.31', category: 'その他収入', value: 4, percentage: 0 },
// ]
//
// export const outTransactions: Transaction[] = [
//   { id: '機関紙発送費1', date: '2021.01.05', category: '機関紙誌発行費', value: 165009, percentage: 20 },
//   { id: '機関紙発送費2', date: '2021.08.05', category: '機関紙誌発行費', value: 158862, percentage: 20 },
//   { id: '資金管理団体通信費', date: '2021.02.22', category: '事務所費', value: 29350, percentage: 4 },
//   { id: '事務所費年間', date: '2021.12.06', category: '事務所費', value: 24000, percentage: 3 },
//   { id: '資金管理団体大会費', date: '2021.02.06', category: '組織活動費', value: 87740, percentage: 11 },
//   { id: '資金管理団体印刷費1', date: '2021.07.30', category: '機関紙誌発行費', value: 154000, percentage: 19 },
//   { id: '資金管理団体印刷費2', date: '2021.12.21', category: '機関紙誌発行費', value: 154000, percentage: 19 },
//   { id: 'その他の大会費', date: '2021.12.31', category: '組織活動費', value: 13693, percentage: 2 },
// ]

