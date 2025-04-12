import {BoardContainer} from '@/components/BoardContainer'
import {Avatar, HStack, Stack, Text} from '@chakra-ui/react'

export function BoardProfile() {
  return (
    <BoardContainer>
      <HStack alignItems={'center'} gap={5}>
        <HStack gap={5} minW={'250px'}>
          <Avatar.Root w={'50px'} h={'50px'}>
            <Avatar.Fallback name={'政治 太郎'}/>
            <Avatar.Image src={'//i.pravatar.cc/200?u=2'}/>
          </Avatar.Root>
          <Stack gap={0}>
            <Text fontSize={'xs'}>{'衆議院議員'}</Text>
            <Text fontSize={'2xl'} fontWeight={'bold'}>{'政治 太郎'}</Text>
          </Stack>
        </HStack>
      </HStack>
    </BoardContainer>
  )
}
