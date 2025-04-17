import {Box} from '@chakra-ui/react'
import {BoardMetadata} from '@/components/BoardMetadata'
import {BoardSummary} from '@/components/BoardSummary'
import {Header} from '@/components/Header'
import {Footer} from '@/components/Footer'
import {BoardProfile} from '@/components/BoardProfile'
import {BoardTransactions} from '@/components/BoardTransactions'

import example from '@/data/example'

export async function generateStaticParams() {
  const slugs = [
    'example'
  ]
  return slugs.map(slug => ({slug}))
}

async function getData(slug: string) {
  switch (slug) {
    case 'example':
      return example
    default:
      throw new Error('not found')
  }
}

type PageProps = {
  params: Promise<{
    slug: string
  }>
}

export default async function Page({ params }: PageProps) {
  const slug = (await params).slug
  const data = await getData(slug)
  return (
    <Box>
      <Header />
      <BoardProfile profile={data.profile} supports={data.supports} />
      <BoardSummary summary={data.summary} flows={data.flows} />
      <BoardTransactions direction={'income'} transactions={data.incomeTransactions} />
      <BoardTransactions direction={'expense'} transactions={data.expenseTransactions} />
      <BoardMetadata metadata={data.metadata} />
      <Footer />
    </Box>
  )
}
