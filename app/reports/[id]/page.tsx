import fs from 'node:fs';
import path from 'node:path';
import { BoardMetadata } from '@/components/BoardMetadata';
import { BoardSummary } from '@/components/BoardSummary';
import { BoardTransactions } from '@/components/BoardTransactions';
import { Footer } from '@/components/Footer';
import { Header } from '@/components/Header';
import { Notice } from '@/components/Notice';
import type { Flow, Profile, Report, Transaction } from '@/models/type';
import { Box } from '@chakra-ui/react';
import { notFound } from 'next/navigation';

interface ReportData {
  id: string;
  profile: Profile;
  report: Report;
  reports: Report[];
  flows: Flow[];
  incomeTransactions: Transaction[];
  expenseTransactions: Transaction[];
}

async function getReportData(id: string): Promise<ReportData | null> {
  try {
    const filePath = path.join(
      process.cwd(),
      'public',
      'reports',
      `${id}.json`,
    );
    const fileContents = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(fileContents);
  } catch (error) {
    console.error('Error loading report data:', error);
    return null;
  }
}

export async function generateStaticParams() {
  const reportsDirectory = path.join(process.cwd(), 'public', 'reports');

  try {
    const filenames = fs.readdirSync(reportsDirectory);

    return filenames
      .filter((name) => name.endsWith('.json'))
      .map((name) => ({
        id: name.replace('.json', ''),
      }));
  } catch (error) {
    console.error('Error reading reports directory:', error);
    return [];
  }
}

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const data = await getReportData(id);

  if (!data) {
    notFound();
  }

  return (
    <Box>
      <Header />
      <BoardSummary
        profile={data.profile}
        report={data.report}
        otherReports={data.reports}
        flows={data.flows}
        useFixedBoardChart={true}
      />
      <BoardTransactions
        direction={'income'}
        total={data.report.totalIncome}
        transactions={data.incomeTransactions}
      />
      <BoardTransactions
        direction={'expense'}
        total={data.report.totalExpense}
        transactions={data.expenseTransactions}
      />
      <BoardMetadata report={data.report} />
      <Notice />
      <Footer />
    </Box>
  );
}
