import {Box, Heading, HStack, Image, Stack} from '@chakra-ui/react'
import {BoardSummary} from '@/components/BoardSummary'
import {BoardChart} from '@/components/BoardChart'
import {BoardBalance} from '@/components/BoardBalance'
import {Footer} from '@/components/Footer'
import {summary, flows, inTransactions,outTransactions } from '@/app/data'

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
