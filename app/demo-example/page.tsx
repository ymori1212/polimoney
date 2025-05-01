import {Box} from '@chakra-ui/react'
import {BoardMetadata} from '@/components/BoardMetadata'
import {BoardSummary} from '@/components/BoardSummary'
import {Header} from '@/components/Header'
import {Footer} from '@/components/Footer'
import {BoardTransactions} from '@/components/BoardTransactions'
import data from '@/data/demo-example'
import {Notice} from '@/components/Notice'

export default async function Page() {
  return (
    <Box>
      <Header />
      <BoardSummary profile={data.profile} report={data.report} otherReports={data.reports} flows={data.flows} />
      <BoardTransactions
        direction={'income'}
        total={data.report.totalIncome}
        transactions={data.transactions.filter(t => t.direction === '収入')}
      />
      <BoardTransactions
        direction={'expense'}
        total={data.report.totalExpense}
        transactions={data.transactions.filter(t => t.direction === '支出')}
      />
      <BoardMetadata report={data.report} />
      <Notice />
      <Footer />
    </Box>
  )
}
