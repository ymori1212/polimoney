'use client'

import {BoardContainer} from '@/components/BoardContainer'
import {Box, HStack, Tabs, Text} from '@chakra-ui/react'
import {BanknoteArrowDownIcon} from 'lucide-react'
import {useState} from 'react'

export function BoardIncome() {

  const [selectedTab, setSelectedTab] = useState('category')

  return (
    <BoardContainer id={'income'}>
      {/* タイトル */}
      <Box mb={5}>
        <HStack mb={2}>
          <HStack fontSize={'xl'} fontWeight={'bold'}>
            <BanknoteArrowDownIcon size={28} className={'income'} />
            <Text>収入の一覧</Text>
          </HStack>
        </HStack>
        <Text fontSize={'sm'} color={'#858585'}>どうやって政治資金を得ているか</Text>
      </Box>
      {/* タブ */}
      <Box mb={5}>
        <Tabs.Root
          value={selectedTab}
          onValueChange={(e) => setSelectedTab(e.value)}
        >
          <Tabs.List>
            <Tabs.Trigger
              value="category"
              fontWeight={'bold'}
              className={selectedTab === 'category' ? 'income' : ''}
            >
              カテゴリー別
            </Tabs.Trigger>
            <Tabs.Trigger
              value="income"
              fontWeight={'bold'}
              className={selectedTab === 'income' ? 'income' : ''}
            >
              収入元別
            </Tabs.Trigger>
          </Tabs.List>
        </Tabs.Root>
      </Box>
    </BoardContainer>
  )
}
