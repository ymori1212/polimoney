import { BoardMetadata } from '@/components/BoardMetadata';
import { BoardSummary } from '@/components/BoardSummary';
import { BoardTransactions } from '@/components/BoardTransactions';
import { Footer } from '@/components/Footer';
import { Header } from '@/components/Header';
import { Notice } from '@/components/Notice';
import data from '@/data/demo-example';
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
      <BoardTransactions
        direction={'income'}
        total={data.report.totalIncome}
        transactions={data.transactions.filter((t) => t.direction === '収入')}
      />
      <BoardTransactions
        direction={'expense'}
        total={data.report.totalExpense}
        transactions={data.transactions.filter((t) => t.direction === '支出')}
      />
      <BoardMetadata report={data.report} />
      <Notice />
      <Footer />
    </Box>
  );
}
