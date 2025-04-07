'use client'

import {Box, Button, Drawer, HStack, Portal, Text, VStack} from '@chakra-ui/react'
import {ExternalLinkIcon} from 'lucide-react'
import Link from 'next/link'

export function Footer() {
  return (
    <VStack my={12}>
      <Drawer.Root placement={'bottom'}>
        <Drawer.Trigger>
          <Text
            className={'textLink'}
            cursor={'pointer'}
            fontSize={'sm'}
            borderBottom={'1px dashed #777'}
          >デジタル民主主義2030プロジェクトについて</Text>
        </Drawer.Trigger>
        <Portal>
          <Drawer.Backdrop/>
          <Drawer.Positioner>
            <Drawer.Content
              p={5}
              roundedTop={'l3'}
            >
              <Drawer.Header>
                <Drawer.Title
                  fontSize={'xl'}
                  fontWeight={'bold'}
                  textAlign={'center'}
                  className={'gradientColor'}
                >デジタル民主主義2030プロジェクトについて</Drawer.Title>
              </Drawer.Header>
              <Drawer.Body textAlign={'center'}>
                <Box mb={8} maxW={'700px'} mx={'auto'}>
                  <Text>
                    2030年には、情報技術により民主主義のあり方はアップデートされており、一人ひとりの声が政治・行政に届き、適切に合意形成・政策反映されていくような社会が当たり前になる──そんな未来を目指して立ち上げられたのがデジタル民主主義2030プロジェクトです。
                    AIやデジタル技術の進化により、これまで不可能だった新しい形の市民参加や政策運営が可能になるはずだという信念に基づいています。
                  </Text>
                  <Link
                    href={'https://dd2030.org'}
                    target={'_blank'}
                    rel={'noreferrer noopener'}
                  >
                    <HStack justify={'center'} mt={4} fontWeight={'bold'}>
                      <Text className={'textLink'}>プロジェクトについての詳細はこちら</Text>
                      <ExternalLinkIcon/>
                    </HStack>
                  </Link>
                </Box>
                <Drawer.ActionTrigger>
                  <Button variant={'outline'}>閉じる</Button>
                </Drawer.ActionTrigger>
              </Drawer.Body>
            </Drawer.Content>
          </Drawer.Positioner>
        </Portal>
      </Drawer.Root>
    </VStack>
  )
}
