'use client'

import {Badge, Box, Heading, HStack, Progress, Text, VStack} from '@chakra-ui/react'
import {Transaction} from '@/type'

type Props = {
  transactions: Transaction[]
  direction: 'in' | 'out'
}

export function BoardBalance({transactions, direction}: Props) {
  return (
    <Box
      bgColor={'#fafafa'}
      borderRadius={'20px'}
      w={'full'}
      p={8}
      boxShadow={'sm'}
      border={'none'}
    >
      <Heading size={'md'} mb={5}>主な{direction === 'in' ? '収入' : '支出'}</Heading>

      <VStack gap={4} align="stretch">
        {transactions.map((transaction) => (
          <Box key={transaction.id}>
            <HStack justify={'space-between'} alignItems={'flex-end'} mb={1}>
              <VStack gap={0} align="flex-start">
                <HStack>
                  <Badge variant={'outline'} size={'sm'}>
                    {transaction.category}
                  </Badge>
                  <Text color="gray.500" fontSize="xs">
                    {transaction.date}
                  </Text>
                </HStack>
                <Text fontWeight="bold" ml={1}>
                  {transaction.id}
                </Text>
              </VStack>
              <HStack>
                <Text fontWeight="bold" fontSize={'lg'}>
                  {transaction.value.toLocaleString()}
                </Text>
                <Text as={'span'} fontSize="xs" color="gray.500">円</Text>
              </HStack>
            </HStack>
            <Progress.Root
              size={'xs'}
              defaultValue={transaction.percentage}
              colorPalette={direction === 'in' ? 'cyan' : 'pink'}
            >
              <HStack gap="5">
                <Progress.Track flex="1">
                  <Progress.Range/>
                </Progress.Track>
                <Progress.ValueText>{transaction.percentage}%</Progress.ValueText>
              </HStack>
            </Progress.Root>
          </Box>
        ))}
      </VStack>
    </Box>
  )
}
