import {BoardContainer} from '@/components/BoardContainer'
import {Avatar, Badge, HStack, NativeSelect, Stack, Text} from '@chakra-ui/react'
import {Profile, Support} from '@/type'

type Props = {
  profile: Profile
  supports: Support[]
}

export function BoardProfile({profile, supports}: Props) {
  return (
    <BoardContainer>
      <Stack
        direction={{base: 'column', lg: 'row'}}
        alignItems={'center'}
        justify={'space-between'}
        gap={5}
      >
        <HStack gap={5} minW={'250px'}>
          <Avatar.Root w={'80px'} h={'80px'}>
            <Avatar.Fallback name={profile.name}/>
            <Avatar.Image src={profile.image}/>
          </Avatar.Root>
          <Stack gap={0}>
            <Text fontSize={'xs'}>{profile.title}</Text>
            <Text fontSize={'2xl'} fontWeight={'bold'}>{profile.name}</Text>
            <HStack mt={1}>
              <Badge variant={'outline'} colorPalette={'red'}>{profile.party}</Badge>
              {profile.district && (<Badge variant={'outline'}>{profile.district}</Badge>)}
            </HStack>
          </Stack>
        </HStack>
        <NativeSelect.Root w={'300px'}>
          <NativeSelect.Field>
            {supports.map((support) => (
              <option key={support.id} value={support.id}>{support.name}</option>
            ))}
          </NativeSelect.Field>
          <NativeSelect.Indicator />
        </NativeSelect.Root>
      </Stack>
    </BoardContainer>
  )
}
