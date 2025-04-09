import {Badge, Box, Card, HStack, Image, SimpleGrid, Stack, Text} from '@chakra-ui/react'
import Link from 'next/link'

const results = ['example']

export default function Page() {
  return (
    <SimpleGrid columns={{ base: 1, lg: 2 }} gap={5}>
      {results.map((result) => (
        <Link href={`/${result}`} key={result}>
          <Card.Root
            flexDirection={'row'}
            boxShadow={'sm'}
            border={'none'}
          >
            <Image
              objectFit="cover"
              maxW="150px"
              src="https://i.pravatar.cc/300?u=2"
              alt="example"
              borderTopLeftRadius="md"
              borderBottomLeftRadius="md"
            />
            <Box>
              <Card.Body>
                <Stack gap={0}>
                  <Text fontSize={'xs'}>衆議院議員</Text>
                  <Text fontSize={'2xl'} fontWeight={'bold'}>政治資金太郎</Text>
                  <Text fontSize={'xs'}>政治資金太郎をみまもる会</Text>
                  <HStack mt={1}>
                    <Badge variant={'outline'} colorPalette={'red'}>政治資金党</Badge>
                    <Badge variant={'outline'}>東京１区</Badge>
                  </HStack>
                </Stack>
              </Card.Body>
            </Box>
          </Card.Root>
        </Link>
      ))}
    </SimpleGrid>
  )
}
