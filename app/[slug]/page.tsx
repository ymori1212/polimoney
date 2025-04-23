import {Box} from '@chakra-ui/react'
import {BoardMetadata} from '@/components/BoardMetadata'
import {BoardSummary} from '@/components/BoardSummary'
import {Header} from '@/components/Header'
import {Footer} from '@/components/Footer'
import {BoardTransactions} from '@/components/BoardTransactions'

import demoTakahiroAnno2024 from '@/data/demo-takahiroanno'
import demoRyosukeIdei2024 from '@/data/demo-ryosukeidei'

export async function generateStaticParams() {
  const slugs = [
    'demo-takahiro-anno-2024',
    'demo-ryosuke-idei-2024',
  ]
  return slugs.map(slug => ({slug}))
}

async function getData(slug: string) {
  switch (slug) {
    case 'demo-takahiro-anno-2024':
      return demoTakahiroAnno2024
    case 'demo-ryosuke-idei-2024':
      return demoRyosukeIdei2024
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
      <BoardSummary profile={data.profile} supports={data.supports} summary={data.summary} flows={data.flows} />
      <BoardTransactions direction={'income'} transactions={data.incomeTransactions} />
      <BoardTransactions direction={'expense'} transactions={data.expenseTransactions} />
      <BoardMetadata metadata={data.metadata} />
      <Footer />
    </Box>
  )
}
