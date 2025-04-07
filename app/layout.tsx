import type {Metadata} from 'next'
import {Provider} from '@/components/ui/provider'

export const metadata: Metadata = {
  title: '政治資金見える化ボード',
  description: '政治資金見える化ボードは、デジタル民主主義2030プロジェクトの一環として、政治資金の透明性を高めるために開発されたオープンソースのプロジェクトです。',
}

export default function RootLayout({children}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ja" suppressHydrationWarning>
      <body>
        <Provider>
          {children}
        </Provider>
      </body>
    </html>
  )
}
