import {Box} from '@chakra-ui/react'
import {BoardMetadata} from '@/components/BoardMetadata'
import {BoardSummary} from '@/components/BoardSummary'
import {Header} from '@/components/Header'
import {Footer} from '@/components/Footer'
import {BoardProfile} from '@/components/BoardProfile'
import {expenseTransactions, flows, incomeTransactions, metadata, profile, summary, supports} from '@/data/example'
import {BoardTransactions} from '@/components/BoardTransactions'

export async function generateStaticParams() {
  const slugs = ['example']
  return slugs.map(slug => ({slug}))
}

export default function Page() {
  return (
    <Box>
      <Header />
      <BoardProfile profile={profile} supports={supports} />
      <BoardSummary summary={summary} flows={flows} />
      <BoardTransactions direction={'income'} transactions={incomeTransactions} />
      <BoardTransactions direction={'expense'} transactions={expenseTransactions} />
      <BoardMetadata metadata={metadata} />
      <Footer />
    </Box>
  )
}
