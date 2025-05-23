import { BoardMetadata } from '@/components/BoardMetadata';
import { BoardOldTransactions } from '@/components/BoardOldTransactions';
import { BoardSummary } from '@/components/BoardSummary';
import { Footer } from '@/components/Footer';
import { Header } from '@/components/Header';
import { Notice } from '@/components/Notice';
import data from '@/data/demo-takahiroanno';
import { Box } from '@chakra-ui/react';

export default async function Page() {
  return (
    <Box>
      <Header />
      <BoardSummary
        profile={data.profile}
        report={data.report}
        otherReports={data.reports}
        flows={data.flows}
      />
      <BoardOldTransactions
        direction={'income'}
        transactions={data.incomeTransactions}
      />
      <BoardOldTransactions
        direction={'expense'}
        transactions={data.expenseTransactions}
      />
      <BoardMetadata report={data.report} />
      <Notice />
      <Footer />
    </Box>
  );
}
