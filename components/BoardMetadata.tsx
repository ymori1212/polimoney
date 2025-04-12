import {BoardContainer} from '@/components/BoardContainer'
import {HStack, SimpleGrid, Text} from '@chakra-ui/react'

export function BoardMetadata() {
  return (
    <BoardContainer>
      <Text fontSize={'sm'} fontWeight={'bold'} mb={4}>
        本収支報告に関する情報開示
      </Text>
      <SimpleGrid columns={{base: 1, md: 2}} gap={2}>
        <HStack>
          <dt>データ引用元</dt>
          <dd>2024年政治資金収支報告書</dd>
        </HStack>
        <HStack>
          <dt>政治団体の区分</dt>
          <dd>その他の政治団体</dd>
        </HStack>
        <HStack>
          <dt>政治団体の名称</dt>
          <dd>政治太郎講演会</dd>
        </HStack>
        <HStack>
          <dt>活動区域の区分</dt>
          <dd>２以上の都道府県の区域など</dd>
        </HStack>
        <HStack>
          <dt>代表者</dt>
          <dd>政治太郎</dd>
        </HStack>
        <HStack>
          <dt>資金管理団体の指定</dt>
          <dd>有り/衆議院議員(現職)政治太郎</dd>
        </HStack>
        <HStack>
          <dt>会計責任者</dt>
          <dd>中村太郎</dd>
        </HStack>
        <HStack>
          <dt>最終更新日</dt>
          <dd>2025.3.31</dd>
        </HStack>
        <HStack>
          <dt>事務担当者</dt>
          <dd>中村太郎</dd>
        </HStack>
      </SimpleGrid>
    </BoardContainer>
  )
}
