import { Box } from '@chakra-ui/react';

type Props = {
  id?: string;
  children: React.ReactNode;
};

export function BoardContainer({ id, children }: Props) {
  return (
    <Box id={id} bgColor={'#ffffff'} borderRadius={'xl'} px={10} py={8} mb={6}>
      {children}
    </Box>
  );
}
