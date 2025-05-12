'use client';

import { BoardContainer } from '@/components/BoardContainer';
import type { Transaction } from '@/models/type';
import {
  Badge,
  Box,
  ButtonGroup,
  HStack,
  IconButton,
  Pagination,
  Progress,
  Table,
  Text,
  VStack,
} from '@chakra-ui/react';
import {
  BanknoteArrowDownIcon,
  BanknoteArrowUpIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from 'lucide-react';
import { useState } from 'react';

type Props = {
  direction: 'income' | 'expense';
  total: number;
  transactions: Transaction[];
};

export function BoardTransactions({ direction, total, transactions }: Props) {
  // const [selectedTab, setSelectedTab] = useState('name')
  const [page, setPage] = useState(1);
  const pageSize = 10;

  // 現在のページに表示する transactions を計算
  const sorted = transactions.sort((a, b) => b.amount - a.amount);
  const paginated = sorted.slice((page - 1) * pageSize, page * pageSize);

  return (
    <BoardContainer id={direction}>
      {/* タイトル */}
      <Box mb={5}>
        <HStack mb={2}>
          <HStack fontSize={'xl'} fontWeight={'bold'}>
            {direction === 'income' ? (
              <BanknoteArrowUpIcon size={28} className={direction} />
            ) : (
              <BanknoteArrowDownIcon size={28} className={direction} />
            )}
            <Text>{direction === 'income' ? '収入' : '支出'}の一覧</Text>
          </HStack>
        </HStack>
        <Text fontSize={'sm'} color={'#858585'}>
          {direction === 'income'
            ? 'どうやって政治資金を得ているか'
            : '政治資金を何に使っているか'}
        </Text>
      </Box>
      {/* タブ */}
      {/*<Box mb={5}>*/}
      {/*  <Tabs.Root*/}
      {/*    value={selectedTab}*/}
      {/*    onValueChange={(e) => setSelectedTab(e.value)}*/}
      {/*  >*/}
      {/*    <Tabs.List>*/}
      {/*      <Tabs.Trigger*/}
      {/*        value="name"*/}
      {/*        fontWeight={'bold'}*/}
      {/*        className={selectedTab === 'name' ? direction : ''}*/}
      {/*      >*/}
      {/*        {direction === 'income' ? '収入元' : '支出先'}別*/}
      {/*      </Tabs.Trigger>*/}
      {/*      <Tabs.Trigger*/}
      {/*        value="category"*/}
      {/*        fontWeight={'bold'}*/}
      {/*        className={selectedTab === 'category' ? direction : ''}*/}
      {/*      >*/}
      {/*        カテゴリー別*/}
      {/*      </Tabs.Trigger>*/}
      {/*      {direction === 'expense' && (*/}
      {/*        <Tabs.Trigger*/}
      {/*          value="purpose"*/}
      {/*          fontWeight={'bold'}*/}
      {/*          className={selectedTab === 'purpose' ? direction : ''}*/}
      {/*        >*/}
      {/*          目的別*/}
      {/*        </Tabs.Trigger>*/}
      {/*      )}*/}
      {/*    </Tabs.List>*/}
      {/*  </Tabs.Root>*/}
      {/*</Box>*/}
      {/* テーブル (smartphone) */}
      <Box display={{ base: 'block', lg: 'none' }} mb={5}>
        {paginated.map((item) => (
          <HStack key={item.id} borderBottom={'1px solid #E2E8F0'} py={4}>
            <Box w={'full'}>
              <HStack mb={2}>
                <Badge>
                  {item.category}：{item.subCategory}
                </Badge>
                <Text fontSize={'xs'}>{item.date}</Text>
              </HStack>
              {direction === 'expense' && (
                <Text fontSize={'xs'} fontWeight={'bold'}>
                  {item.purpose}
                </Text>
              )}
              <HStack justifyContent={'space-between'} mb={1}>
                <Text fontWeight={'bold'}>{item.name}</Text>
                <Text fontWeight={'bold'}>{item.amount.toLocaleString()}</Text>
              </HStack>
              <Progress.Root
                defaultValue={(item.amount / total) * 100}
                size={'xs'}
                colorPalette={direction === 'income' ? 'cyan' : 'pink'}
              >
                <HStack gap="5">
                  <Progress.Track flex="1">
                    <Progress.Range />
                  </Progress.Track>
                  <Progress.ValueText w={'40px'}>
                    {((item.amount / total) * 100).toFixed(1)}%
                  </Progress.ValueText>
                </HStack>
              </Progress.Root>
            </Box>
            {/*<IconButton variant={'ghost'} size={'xs'}>*/}
            {/*  <CircleChevronDownIcon className={direction} />*/}
            {/*</IconButton>*/}
          </HStack>
        ))}
      </Box>
      {/* テーブル (laptop) */}
      <Box display={{ base: 'none', lg: 'block' }} mb={5}>
        <Table.Root size={'lg'}>
          <Table.Header>
            <Table.Row fontSize={'sm'}>
              {direction === 'expense' && (
                <Table.ColumnHeader fontWeight={'bold'}>
                  目的
                </Table.ColumnHeader>
              )}
              <Table.ColumnHeader fontWeight={'bold'}>
                {direction === 'income' ? '収入元' : '支出先'}
              </Table.ColumnHeader>
              <Table.ColumnHeader fontWeight={'bold'}>
                カテゴリー
              </Table.ColumnHeader>
              <Table.ColumnHeader fontWeight={'bold'} textAlign="end">
                金額
              </Table.ColumnHeader>
              <Table.ColumnHeader fontWeight={'bold'}>割合</Table.ColumnHeader>
              <Table.ColumnHeader fontWeight={'bold'}>日付</Table.ColumnHeader>
              {/*<Table.ColumnHeader w={'32px'} />*/}
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {paginated.map((item) => (
              <Table.Row key={item.id} fontSize={'sm'}>
                {direction === 'expense' && (
                  <Table.Cell fontWeight={'bold'}>{item.purpose}</Table.Cell>
                )}
                <Table.Cell fontWeight={'bold'}>{item.name}</Table.Cell>
                <Table.Cell>
                  <Badge>
                    {item.category}：{item.subCategory}
                  </Badge>
                </Table.Cell>
                <Table.Cell fontWeight={'bold'} textAlign="end">
                  {item.amount.toLocaleString()}
                </Table.Cell>
                <Table.Cell minW={'150px'}>
                  <Progress.Root
                    defaultValue={(item.amount / total) * 100}
                    size={'xs'}
                    colorPalette={direction === 'income' ? 'cyan' : 'pink'}
                  >
                    <HStack gap="5">
                      <Progress.Track flex="1">
                        <Progress.Range />
                      </Progress.Track>
                      <Progress.ValueText>
                        {((item.amount / total) * 100).toFixed(1)}%
                      </Progress.ValueText>
                    </HStack>
                  </Progress.Root>
                </Table.Cell>
                <Table.Cell>{item.date}</Table.Cell>
                {/*<Table.Cell>*/}
                {/*  <IconButton variant={'ghost'} size={'xs'}>*/}
                {/*    <CircleChevronDownIcon className={direction} />*/}
                {/*  </IconButton>*/}
                {/*</Table.Cell>*/}
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
  );
}
