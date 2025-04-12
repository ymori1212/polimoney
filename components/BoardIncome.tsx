'use client'

import {BoardContainer} from '@/components/BoardContainer'
import {Box, HStack, Table, Tabs, Text} from '@chakra-ui/react'
import {BanknoteArrowDownIcon} from 'lucide-react'
import {useState} from 'react'
import {inTransactions} from '@/data/example'

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
            {inTransactions.map((item) => (
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
