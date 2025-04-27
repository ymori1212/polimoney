import type {Metadata} from 'next'
import {Provider} from '@/components/ui/provider'
import {Box} from '@chakra-ui/react'
import './global.css'

export const metadata: Metadata = {
  title: 'Polimoney (ポリマネー)',
  description: 'Polimoney (ポリマネー) は、デジタル民主主義2030プロジェクトの一環として、政治資金の透明性を高めるために開発されたオープンソースのプロジェクトです。',
  metadataBase: new URL(
    process.env.NODE_ENV === 'production'
      ? 'https://polimoney.dd2030.org'
      : 'http://localhost:3000'
  ),
}

export default function RootLayout({children}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ja" suppressHydrationWarning>
      <body>
        <Provider>
          <Box maxW="1100px" mx="auto" p={{base: 5, lg: 10}}>
            {children}
          </Box>
        </Provider>
      </body>
    </html>
  )
}
