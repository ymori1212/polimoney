import {Box, Stack} from '@chakra-ui/react'
import {BoardSummary} from '@/components/BoardSummary'
import {BoardChart} from '@/components/BoardChart'
import {BoardBalance} from '@/components/BoardBalance'
import {summary, flows, inTransactions,outTransactions } from '@/data/example'

export async function generateStaticParams() {
  const slugs = ['example']
  return slugs.map(slug => ({slug}))
}

export default function Page() {
  return (
    <Box>
      <BoardSummary summary={summary}/>
      <BoardChart flows={flows}/>
      <Stack direction={{base: 'column', lg: 'row'}} gap={5} mb={5}>
        <BoardBalance direction={'in'} transactions={inTransactions}/>
        <BoardBalance direction={'out'} transactions={outTransactions}/>
      </Stack>
    </Box>
  )
}
