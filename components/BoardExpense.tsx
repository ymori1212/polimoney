'use client'

import {BoardContainer} from '@/components/BoardContainer'
import {Box, HStack, Tabs, Text} from '@chakra-ui/react'
import {BanknoteArrowUpIcon} from 'lucide-react'
import {useState} from 'react'

export function BoardExpense() {

  const [selectedTab, setSelectedTab] = useState('category')

  return (
    <BoardContainer id={'expense'}>
      {/* タイトル */}
      <Box mb={5}>
        <HStack mb={2}>
          <HStack fontSize={'xl'} fontWeight={'bold'}>
            <BanknoteArrowUpIcon size={28} className={'expense'}/>
            <Text>支出の一覧</Text>
          </HStack>
        </HStack>
        <Text fontSize={'sm'} color={'#858585'}>政治資金を何に使っているか</Text>
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
              className={selectedTab === 'category' ? 'expense' : ''}
            >
              カテゴリー別
            </Tabs.Trigger>
            <Tabs.Trigger
              value="expense"
              fontWeight={'bold'}
              className={selectedTab === 'expense' ? 'expense' : ''}
            >
              支出先別
            </Tabs.Trigger>
          </Tabs.List>
        </Tabs.Root>
      </Box>
    </BoardContainer>
  )
}
