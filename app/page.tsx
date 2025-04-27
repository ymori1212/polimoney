import {Badge, Box, Card, HStack, Image, SimpleGrid, Stack, Text} from '@chakra-ui/react'
import {Header} from '@/components/Header'
import {Footer} from '@/components/Footer'
import Link from 'next/link'
import demoTakahiroAnno2024 from '@/data/demo-takahiroanno'
import demoRyosukeIdei2024 from '@/data/demo-ryosukeidei'

const results = [
  demoTakahiroAnno2024,
  demoRyosukeIdei2024
]

export const metadata = {
  title: 'Polimoney - 政治資金の透明性を高める',
  description: 'Polimoneyは、デジタル民主主義2030プロジェクトの一環として、政治資金の透明性を高めるために開発されたオープンソースのプロジェクトです。',
  openGraph: {
    title: 'Polimoney - 政治資金の透明性を高める',
    description: 'Polimoneyは、デジタル民主主義2030プロジェクトの一環として、政治資金の透明性を高めるために開発されたオープンソースのプロジェクトです。',
    url: 'https://polimoney.example.com',
    type: 'website',
  },
  twitter: {
    card: 'summary',
    title: 'Polimoney - 政治資金の透明性を高める',
    description: 'Polimoneyは、デジタル民主主義2030プロジェクトの一環として、政治資金の透明性を高めるために開発されたオープンソースのプロジェクトです。',
  },
};

export default function Page() {
  return (
    <Box>
      <Header />
      <SimpleGrid columns={{ base: 1, lg: 2 }} gap={5} mb={5} p={2}>
        {results.map((result) => (
          <Link href={`/${result.id}`} key={result.id}>
            <Card.Root
              flexDirection={'row'}
              boxShadow={'xs'}
              border={'none'}
            >
              <Image
                objectFit="cover"
                maxW="130px"
                src={result.profile.image}
                alt={result.profile.name}
                borderTopLeftRadius="md"
                borderBottomLeftRadius="md"
              />
              <Box>
                <Card.Body>
                  <Stack gap={0}>
                    <Text fontSize={'xs'}>{result.profile.title}</Text>
                    <Text fontSize={'2xl'} fontWeight={'bold'}>{result.profile.name}</Text>
                    <HStack mt={1}>
                      <Badge variant={'outline'} colorPalette={'red'}>{result.profile.party}</Badge>
                      {result.profile.district && (<Badge variant={'outline'}>{result.profile.district}</Badge>)}
                    </HStack>
                  </Stack>
                </Card.Body>
              </Box>
            </Card.Root>
          </Link>
        ))}
      </SimpleGrid>
      <Footer />
    </Box>
  )
}
