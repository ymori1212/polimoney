'use client'

import {BoardContainer} from '@/components/BoardContainer'
import {
  Badge,
  Box,
  ButtonGroup,
  HStack,
  IconButton,
  Pagination,
  Progress,
  Table,
  Tabs,
  Text,
  VStack
} from '@chakra-ui/react'
import {BanknoteArrowUpIcon, ChevronLeftIcon, ChevronRightIcon, CircleChevronDownIcon} from 'lucide-react'
import {useState} from 'react'
import {Transaction} from '@/type'

type Props = {
  direction: 'income' | 'expense'
  transactions: Transaction[]
}

export function BoardTransactions({direction, transactions}: Props) {

  const [selectedTab, setSelectedTab] = useState('category')
  const [page, setPage] = useState(1)
  const pageSize = 10

  // 現在のページに表示する transactions を計算
  const paginatedTransactions = transactions.slice((page - 1) * pageSize, page * pageSize)

  return (
    <BoardContainer id={direction}>
      {/* タイトル */}
      <Box mb={5}>
        <HStack mb={2}>
          <HStack fontSize={'xl'} fontWeight={'bold'}>
            <BanknoteArrowUpIcon size={28} className={direction}/>
            <Text>{direction === 'income' ? '収入' : '支出'}の一覧</Text>
          </HStack>
        </HStack>
        <Text fontSize={'sm'} color={'#858585'}>
          {direction === 'income' ? 'どうやって政治資金を得ているか' : '政治資金を何に使っているか'}
        </Text>
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
              className={selectedTab === 'category' ? direction : ''}
            >
              カテゴリー別
            </Tabs.Trigger>
            <Tabs.Trigger
              value="direction"
              fontWeight={'bold'}
              className={selectedTab === 'direction' ? direction : ''}
            >
              {direction === 'income' ? '収入' : '支出'}先別
            </Tabs.Trigger>
          </Tabs.List>
        </Tabs.Root>
      </Box>
      {/* テーブル */}
      <Box>
        <Table.Root size={'lg'}>
          <Table.Header>
            <Table.Row fontSize={'sm'}>
              <Table.ColumnHeader fontWeight={'bold'}>{direction === 'income' ? '収入' : '支出'}項目</Table.ColumnHeader>
              <Table.ColumnHeader fontWeight={'bold'}>カテゴリー</Table.ColumnHeader>
              <Table.ColumnHeader fontWeight={'bold'}>金額</Table.ColumnHeader>
              <Table.ColumnHeader fontWeight={'bold'}>割合</Table.ColumnHeader>
              <Table.ColumnHeader fontWeight={'bold'}>日付</Table.ColumnHeader>
              <Table.ColumnHeader w={'50px'} />
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {paginatedTransactions.map((item) => (
              <Table.Row key={item.id} fontSize={'sm'}>
                <Table.Cell fontWeight={'bold'}>{item.name}</Table.Cell>
                <Table.Cell>
                  <Badge>{item.category}</Badge>
                </Table.Cell>
                <Table.Cell fontWeight={'bold'}>{item.value.toLocaleString()}</Table.Cell>
                <Table.Cell>
                  <Progress.Root
                    defaultValue={item.percentage}
                    size={'xs'}
                    colorPalette={direction === 'income' ? 'cyan' : 'pink'}
                  >
                    <HStack gap="5">
                      <Progress.Track flex="1">
                        <Progress.Range />
                      </Progress.Track>
                      <Progress.ValueText>{item.percentage}%</Progress.ValueText>
                    </HStack>
                  </Progress.Root>
                </Table.Cell>
                <Table.Cell>{item.date}</Table.Cell>
                <Table.Cell>
                  <CircleChevronDownIcon size={18} className={direction} />
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
      </Box>
      {/* ページネーション */}
      <VStack mt={5}>
        <Pagination.Root
          count={transactions.length}
          pageSize={pageSize}
          page={page}
          onPageChange={(e) => setPage(e.page)}
        >
          <ButtonGroup variant="ghost" size="sm">
            <Pagination.PrevTrigger asChild>
              <IconButton>
                <ChevronLeftIcon />
              </IconButton>
            </Pagination.PrevTrigger>
            <Pagination.Items
              render={(page) => (
                <IconButton variant={{ base: 'ghost', _selected: 'outline' }}>
                  {page.value}
                </IconButton>
              )}
            />
            <Pagination.NextTrigger asChild>
              <IconButton>
                <ChevronRightIcon />
              </IconButton>
            </Pagination.NextTrigger>
          </ButtonGroup>
        </Pagination.Root>
      </VStack>
    </BoardContainer>
  )
}
