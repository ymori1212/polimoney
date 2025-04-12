import {Box} from '@chakra-ui/react'
import {BoardMetadata} from '@/components/BoardMetadata'
import {BoardIncome} from '@/components/BoardIncome'
import {BoardExpense} from '@/components/BoardExpense'
import {BoardSummary} from '@/components/BoardSummary'
import {Header} from '@/components/Header'
import {Footer} from '@/components/Footer'
import {BoardProfile} from '@/components/BoardProfile'
import {metadata} from '@/data/example'

export async function generateStaticParams() {
  const slugs = ['example']
  return slugs.map(slug => ({slug}))
}

export default function Page() {
  return (
    <Box>
      <Header />
      <BoardProfile />
      <BoardSummary />
      <BoardIncome />
      <BoardExpense />
      <BoardMetadata metadata={metadata} />
      <Footer />
    </Box>
  )
}
