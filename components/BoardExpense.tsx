'use client'

import {BoardContainer} from '@/components/BoardContainer'
import {Box, HStack, Table, Tabs, Text} from '@chakra-ui/react'
import {BanknoteArrowUpIcon} from 'lucide-react'
import {useState} from 'react'
import {outTransactions} from '@/data/example'

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
      {/* テーブル */}
      <Box>
        <Table.Root size={'lg'}>
          <Table.Header>
            <Table.Row fontSize={'sm'}>
              <Table.ColumnHeader fontWeight={'bold'}>収入項目</Table.ColumnHeader>
              <Table.ColumnHeader fontWeight={'bold'}>カテゴリー</Table.ColumnHeader>
              <Table.ColumnHeader fontWeight={'bold'}>金額</Table.ColumnHeader>
              <Table.ColumnHeader fontWeight={'bold'}>割合</Table.ColumnHeader>
              <Table.ColumnHeader fontWeight={'bold'}>日付</Table.ColumnHeader>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {outTransactions.map((item) => (
              <Table.Row key={item.id} fontSize={'sm'}>
                <Table.Cell>{item.id}</Table.Cell>
                <Table.Cell>{item.category}</Table.Cell>
                <Table.Cell>{item.value}</Table.Cell>
                <Table.Cell>{item.percentage}</Table.Cell>
                <Table.Cell>{item.date}</Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
      </Box>
    </BoardContainer>
  )
}
