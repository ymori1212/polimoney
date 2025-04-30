import {Box} from '@chakra-ui/react'
import {BoardMetadata} from '@/components/BoardMetadata'
import {BoardSummary} from '@/components/BoardSummary'
import {Header} from '@/components/Header'
import {Footer} from '@/components/Footer'
import {BoardOldTransactions} from '@/components/BoardOldTransactions'
import data from '@/data/demo-ryosukeidei'
import {Notice} from '@/components/Notice'

export default async function Page() {
  return (
    <Box>
      <Header />
      <BoardSummary profile={data.profile} sources={data.supports} summary={data.summary} flows={data.flows} />
      <BoardOldTransactions direction={'income'} transactions={data.incomeTransactions} />
      <BoardOldTransactions direction={'expense'} transactions={data.expenseTransactions} />
      <BoardMetadata metadata={data.metadata} />
      <Notice />
      <Footer />
    </Box>
  )
}
