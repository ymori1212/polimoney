'use client';

import { BoardChart } from '@/components/BoardChart';
import { BoardContainer } from '@/components/BoardContainer';
import type { Flow, Profile, Report } from '@/models/type';
import {
  Avatar,
  Badge,
  Box,
  HStack,
  NativeSelect,
  SimpleGrid,
  Stack,
  Stat,
  Text,
} from '@chakra-ui/react';
import { LandmarkIcon } from 'lucide-react';
import { useRouter } from 'next/navigation';

type Props = {
  profile: Profile;
  report: Report;
  otherReports: Report[];
  flows: Flow[];
};

export function BoardSummary({ profile, report, otherReports, flows }: Props) {
  const router = useRouter();
  // const [selectedTab, setSelectedTab] = useState('amount')

  return (
    <BoardContainer id={'summary'}>
      {/* プロフィール */}
      <Box mb={10}>
        <Stack
          direction={{ base: 'column', lg: 'row' }}
          alignItems={'center'}
          justify={'space-between'}
          gap={5}
        >
          <HStack gap={5} minW={'250px'}>
            <Avatar.Root w={'80px'} h={'80px'}>
              <Avatar.Fallback name={profile.name} />
              <Avatar.Image src={profile.image} />
            </Avatar.Root>
            <Stack gap={0}>
              <Text fontSize={'xs'}>{profile.title}</Text>
              <Text fontSize={'2xl'} fontWeight={'bold'}>
                {profile.name}
              </Text>
              <HStack mt={1}>
                <Badge variant={'outline'} colorPalette={'red'}>
                  {profile.party}
                </Badge>
                {profile.district && (
                  <Badge variant={'outline'}>{profile.district}</Badge>
                )}
              </HStack>
            </Stack>
          </HStack>
          <NativeSelect.Root
            w={'300px'}
            defaultValue={report.id}
            onChange={(e) => {
              const target = e.target as HTMLSelectElement;
              router.push(`/${target.value}`);
            }}
          >
            <NativeSelect.Field>
              {otherReports.map((report) => (
                <option key={report.id} value={report.id}>
                  {report.year}年 {report.orgName}
                </option>
              ))}
            </NativeSelect.Field>
            <NativeSelect.Indicator />
          </NativeSelect.Root>
        </Stack>
      </Box>
      {/* タイトル */}
      <Box mb={5}>
        <HStack justify={'space-between'} alignItems={'center'}>
          <HStack fontSize={'xl'} fontWeight={'bold'}>
            <LandmarkIcon size={28} className={'income'} />
            <Text>収支の流れ</Text>
          </HStack>
        </HStack>
      </Box>
      {/* サマリー */}
      <Box mb={5}>
        <SimpleGrid columns={{ base: 1, lg: 3 }} gap={5}>
          <Box
            border={'1px solid #dddddd'}
            borderRadius={'lg'}
            p={5}
            minW={'200px'}
          >
            <Stat.Root>
              <Stat.Label
                className={'income'}
                fontWeight={'bold'}
                fontSize={'sm'}
              >
                収入総額
              </Stat.Label>
              <Stat.ValueText alignItems="baseline" fontSize={'2xl'}>
                {Math.round(report.totalIncome / 10000)}
                <Stat.ValueUnit>万円</Stat.ValueUnit>
              </Stat.ValueText>
            </Stat.Root>
          </Box>
          <Box
            border={'1px solid #dddddd'}
            borderRadius={'lg'}
            p={5}
            minW={'200px'}
          >
            <Stat.Root>
              <Stat.Label
                className={'expense'}
                fontWeight={'bold'}
                fontSize={'sm'}
              >
                支出総額
              </Stat.Label>
              <Stat.ValueText alignItems="baseline" fontSize={'2xl'}>
                {Math.round(report.totalExpense / 10000)}
                <Stat.ValueUnit>万円</Stat.ValueUnit>
              </Stat.ValueText>
            </Stat.Root>
          </Box>
          <Box
            border={'1px solid #dddddd'}
            borderRadius={'lg'}
            p={5}
            minW={'200px'}
          >
            <Stat.Root>
              <Stat.Label fontWeight={'bold'} fontSize={'sm'}>
                年間収支
              </Stat.Label>
              <Stat.ValueText alignItems="baseline" fontSize={'2xl'}>
                {Math.round(report.totalBalance / 10000)}
                <Stat.ValueUnit>万円</Stat.ValueUnit>
              </Stat.ValueText>
            </Stat.Root>
          </Box>
        </SimpleGrid>
      </Box>
      {/* タブ */}
      {/*<Box mb={5}>*/}
      {/*  <Tabs.Root*/}
      {/*    value={selectedTab}*/}
      {/*    onValueChange={(e) => setSelectedTab(e.value)}*/}
      {/*  >*/}
      {/*    <Tabs.List>*/}
      {/*      <Tabs.Trigger*/}
      {/*        value="amount"*/}
      {/*        fontWeight={'bold'}*/}
      {/*        className={selectedTab === 'amount' ? 'income' : ''}*/}
      {/*      >*/}
      {/*        金額(円)*/}
      {/*      </Tabs.Trigger>*/}
      {/*      <Tabs.Trigger*/}
      {/*        value="percentage"*/}
      {/*        fontWeight={'bold'}*/}
      {/*        className={selectedTab === 'percentage' ? 'income' : ''}*/}
      {/*      >*/}
      {/*        割合(%)*/}
      {/*      </Tabs.Trigger>*/}
      {/*    </Tabs.List>*/}
      {/*  </Tabs.Root>*/}
      {/*</Box>*/}
      {/* チャート */}
      <BoardChart flows={flows} />
    </BoardContainer>
  );
}
