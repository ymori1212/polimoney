import {BoardContainer} from '@/components/BoardContainer'
import {HStack, SimpleGrid, Text} from '@chakra-ui/react'
import {Metadata} from '@/models/type'

type Props = {
  metadata: Metadata
}

export function BoardMetadata({metadata}: Props) {
  return (
    <BoardContainer>
      <Text fontSize={'sm'} fontWeight={'bold'} mb={4}>
        本収支報告に関する情報開示
      </Text>
      <SimpleGrid columns={{base: 1, lg: 2}} gap={2}>
        <HStack>
          <dt>データ引用元</dt>
          <dd>{metadata.source}</dd>
        </HStack>
        <HStack>
          <dt>政治団体の区分</dt>
          <dd>{metadata.orgType}</dd>
        </HStack>
        <HStack>
          <dt>政治団体の名称</dt>
          <dd>{metadata.orgName}</dd>
        </HStack>
        <HStack>
          <dt>活動区域の区分</dt>
          <dd>{metadata.activityArea}</dd>
        </HStack>
        <HStack>
          <dt>代表者</dt>
          <dd>{metadata.representative}</dd>
        </HStack>
        <HStack>
          <dt>資金管理団体の指定</dt>
          <dd>{metadata.fundManagementOrg}</dd>
        </HStack>
        <HStack>
          <dt>会計責任者</dt>
          <dd>{metadata.accountingManager}</dd>
        </HStack>
        <HStack>
          <dt>最終更新日</dt>
          <dd>{metadata.lastUpdate}</dd>
        </HStack>
        <HStack>
          <dt>事務担当者</dt>
          <dd>{metadata.administrativeManager}</dd>
        </HStack>
      </SimpleGrid>
    </BoardContainer>
  )
}
