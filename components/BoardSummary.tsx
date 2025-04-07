import {Avatar, Badge, Box, HStack, Separator, Stack, Stat, Text} from '@chakra-ui/react'
import {Summary} from '@/type'

type Props = {
  summary: Summary
}

export function BoardSummary({summary}: Props) {
  return (
    <Box
      bgColor={'#fafafa'}
      borderRadius={'20px'}
      w={'full'}
      mb={5}
      p={6}
      boxShadow={'sm'}
    >
      <Stack direction={{base: 'column', lg: 'row'}} gap={5} alignItems={'center'}>
        <HStack gap={5} minW={'250px'}>
          <Avatar.Root size={'2xl'}>
            <Avatar.Fallback name={summary.name}/>
            <Avatar.Image src="https://i.pravatar.cc/300?u=2"/>
          </Avatar.Root>
          <Stack gap={0}>
            <Text fontSize={'xs'}>{summary.title}</Text>
            <Text fontSize={'2xl'} fontWeight={'bold'}>{summary.name}</Text>
            <Text fontSize={'xs'}>{summary.support}</Text>
            <HStack mt={1}>
              <Badge variant={'outline'} colorPalette={'red'}>{summary.party}</Badge>
              <Badge variant={'outline'}>{summary.district}</Badge>
            </HStack>
          </Stack>
        </HStack>
        <Separator
          orientation={{base: 'horizontal', lg: 'vertical'}}
          w={{base: 'full', lg: '1px'}}
          h={{base: '1px', lg: '80px'}}
        />
        <Stat.Root>
          <Stat.Label>収入総額</Stat.Label>
          <Stat.ValueText alignItems={'baseline'} fontSize={'3xl'}>
            {summary.in.toLocaleString()}<Stat.ValueUnit>円</Stat.ValueUnit>
          </Stat.ValueText>
        </Stat.Root>
        <Separator
          orientation={{base: 'horizontal', lg: 'vertical'}}
          w={{base: 'full', lg: '1px'}}
          h={{base: '1px', lg: '80px'}}
        />
        <Stat.Root>
          <Stat.Label>支出総額</Stat.Label>
          <Stat.ValueText alignItems={'baseline'} fontSize={'3xl'}>
            {summary.out.toLocaleString()}<Stat.ValueUnit>円</Stat.ValueUnit>
          </Stat.ValueText>
        </Stat.Root>
        <Separator
          orientation={{base: 'horizontal', lg: 'vertical'}}
          w={{base: 'full', lg: '1px'}}
          h={{base: '1px', lg: '80px'}}
        />
        <Stat.Root>
          <Stat.Label>翌年繰越額</Stat.Label>
          <Stat.ValueText alignItems={'baseline'} fontSize={'3xl'}>
            {summary.transfer.toLocaleString()}<Stat.ValueUnit>円</Stat.ValueUnit>
          </Stat.ValueText>
        </Stat.Root>
        <Separator
          orientation={{base: 'horizontal', lg: 'vertical'}}
          w={{base: 'full', lg: '1px'}}
          h={{base: '1px', lg: '80px'}}
        />
        <Box w={'80px'}>
          <Stat.Root>
            <Stat.Label>最終更新日</Stat.Label>
            <Stat.ValueText alignItems={'baseline'} fontSize={'xl'}>
              {summary.year}<Stat.ValueUnit>年</Stat.ValueUnit>
            </Stat.ValueText>
          </Stat.Root>
        </Box>
      </Stack>
    </Box>
  )
}
