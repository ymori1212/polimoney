import type {Metadata} from 'next'
import {Provider} from '@/components/ui/provider'
import {Box, Heading, HStack, Image} from '@chakra-ui/react'
import {Footer} from '@/components/Footer'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Moneybook',
  description: 'Moneybook は、デジタル民主主義2030プロジェクトの一環として、政治資金の透明性を高めるために開発されたオープンソースのプロジェクトです。',
}

export default function RootLayout({children}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ja" suppressHydrationWarning>
      <body>
        <Provider>
          <Box maxW="1200px" mx="auto" px={5}>
            <Link href={'/'}>
              <HStack my={6}>
                <Image src="logo.png" alt="Logo" h={'50px'} mr={2}/>
                <Heading>Moneybook</Heading>
              </HStack>
            </Link>
            {children}
            <Footer/>
          </Box>
        </Provider>
      </body>
    </html>
  )
}
