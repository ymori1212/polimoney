import {Box, Heading, HStack, Image, Stack} from '@chakra-ui/react'
import {BoardSummary} from '@/components/BoardSummary'
import {BoardChart} from '@/components/BoardChart'
import {BoardBalance} from '@/components/BoardBalance'
import {Footer} from '@/components/Footer'
import {Flow, Summary, Transaction} from '@/type'

export default function Home() {
  return (
    <Box>
      <Box maxW="1200px" mx="auto" px={5}>
        <HStack my={6}>
          <Image src="logo.png" alt="Logo" h={'50px'} mr={2}/>
          <Heading>政治資金ボード(仮)</Heading>
        </HStack>
        <BoardSummary summary={summary}/>
        <BoardChart flows={flows}/>
        <Stack direction={{base: 'column', lg: 'row'}} gap={5} mb={5}>
          <BoardBalance direction={'in'} transactions={inTransactions}/>
          <BoardBalance direction={'out'} transactions={outTransactions}/>
        </Stack>
      </Box>
      <Footer/>
    </Box>
  )
}

const summary: Summary = {
  name: '政治資金太郎',
  title: '衆議院議員',
  support: '政治資金太郎をみまもる会',
  party: '政治資金党',
  district: '東京1区',
  in: 141180683,
  out: 13262929,
  transfer: 127434080,
  year: 2024,
}

const flows: Flow[] = [
  // 収入
  {id: '個人からの寄付', direction: 'in', value: 1560000, parent: '寄付'},
  {id: '政治団体からの寄付', direction: 'in', value: 100000, parent: '寄付'},
  {id: '寄付', direction: 'in', value: 1660000, parent: '総収入'},
  {id: '機関紙誌の発行その他の事業による収入', direction: 'in', value: 29910000, parent: '総収入'},
  {id: '前年度からの繰越', direction: 'in', value: 109597655, parent: '総収入'},
  // 総収入
  {id: '総収入', direction: 'out', value: 141180683, parent: null},
  // 支出
  {id: '経常経費', direction: 'out', value: 483674, parent: '総収入'},
  {id: '人件費', direction: 'out', value: 57800, parent: '経常経費'},
  {id: '備品・消耗品費', direction: 'out', value: 319314, parent: '経常経費'},
  {id: '事務所費', direction: 'out', value: 106560, parent: '経常経費'},
  {id: '政治活動費', direction: 'out', value: 13262929, parent: '総収入'},
  {id: '組織活動費', direction: 'out', value: 4473026, parent: '政治活動費'},
  {id: '機関紙の発行その他の事業費', direction: 'out', value: 8751150, parent: '政治活動費'},
  {id: '政治資金パーティー開催事業費', direction: 'out', value: 8751150, parent: '機関紙の発行その他の事業費'},
  {id: '調査研究費', direction: 'out', value: 28753, parent: '政治活動費'},
  {id: '寄付・交付金', direction: 'out', value: 10000, parent: '政治活動費'},
  {id: '翌年への繰越', direction: 'out', value: 127434080, parent: '総収入'},
]

const inTransactions: Transaction[] = [
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


const outTransactions: Transaction[] = [
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
