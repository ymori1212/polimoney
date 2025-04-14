'use client'

import {BoardContainer} from '@/components/BoardContainer'
import {Box, HStack, NativeSelect, SimpleGrid, Stat, Tabs, Text} from '@chakra-ui/react'
import {LandmarkIcon} from 'lucide-react'
import {useState} from 'react'
import {BoardChart} from '@/components/BoardChart'
import {Flow, Summary} from '@/type'

type Props = {
  summary: Summary
  flows: Flow[]
}

export function BoardSummary({summary, flows}: Props) {

  const [selectedTab, setSelectedTab] = useState('amount')

  return (
    <BoardContainer id={'summary'}>
      {/* タイトル */}
      <Box mb={5}>
        <HStack justify={'space-between'} alignItems={'center'}>
          <HStack fontSize={'xl'} fontWeight={'bold'}>
            <LandmarkIcon size={28} className={'income'} />
            <Text>収支の流れ</Text>
          </HStack>
          <NativeSelect.Root w={'120px'}>
            <NativeSelect.Field textAlign={'center'}>
              <option value={2024}>2024年</option>
            </NativeSelect.Field>
            <NativeSelect.Indicator />
          </NativeSelect.Root>
        </HStack>
      </Box>
      {/* サマリー */}
      <Box mb={5}>
        <SimpleGrid columns={{base: 1, md: 3}} gap={5}>
          <Box border={'1px solid #dddddd'} borderRadius={'lg'} p={5} minW={'200px'}>
            <Stat.Root>
              <Stat.Label
                className={'income'}
                fontWeight={'bold'}
                fontSize={'sm'}
              >収入総額</Stat.Label>
              <Stat.ValueText alignItems="baseline" fontSize={'2xl'}>
                {Math.round(summary.income / 10000)}
                <Stat.ValueUnit>万円</Stat.ValueUnit>
              </Stat.ValueText>
            </Stat.Root>
          </Box>
          <Box border={'1px solid #dddddd'} borderRadius={'lg'} p={5} minW={'200px'}>
            <Stat.Root>
              <Stat.Label
                className={'expense'}
                fontWeight={'bold'}
                fontSize={'sm'}
              >支出総額</Stat.Label>
              <Stat.ValueText alignItems="baseline" fontSize={'2xl'}>
                {Math.round(summary.expense / 10000)}
                <Stat.ValueUnit>万円</Stat.ValueUnit>
              </Stat.ValueText>
            </Stat.Root>
          </Box>
          <Box border={'1px solid #dddddd'} borderRadius={'lg'} p={5} minW={'200px'}>
            <Stat.Root>
              <Stat.Label
                fontWeight={'bold'}
                fontSize={'sm'}
              >年間収支</Stat.Label>
              <Stat.ValueText alignItems="baseline" fontSize={'2xl'} >
                {Math.round(summary.balance / 10000)}
                <Stat.ValueUnit>万円</Stat.ValueUnit>
              </Stat.ValueText>
            </Stat.Root>
          </Box>
        </SimpleGrid>
      </Box>
      {/* タブ */}
      <Box mb={5}>
        <Tabs.Root
          value={selectedTab}
          onValueChange={(e) => setSelectedTab(e.value)}
        >
          <Tabs.List>
            <Tabs.Trigger
              value="amount"
              fontWeight={'bold'}
              className={selectedTab === 'amount' ? 'income' : ''}
            >
              金額(円)
            </Tabs.Trigger>
            <Tabs.Trigger
              value="percentage"
              fontWeight={'bold'}
              className={selectedTab === 'percentage' ? 'income' : ''}
            >
              割合(%)
            </Tabs.Trigger>
          </Tabs.List>
        </Tabs.Root>
      </Box>
      {/* チャート */}
      <BoardChart flows={flows} />
    </BoardContainer>
  )
}
