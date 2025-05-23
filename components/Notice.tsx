import { Alert } from '@chakra-ui/react';

export function Notice() {
  return (
    <Alert.Root status="info" colorPalette="cyan" mb={6} borderRadius={'lg'}>
      <Alert.Indicator />
      <Alert.Content>
        <Alert.Title fontWeight={'bold'}>開発中</Alert.Title>
        <Alert.Description>
          Polimoney(ポリマネー)は開発中であり、表示内容は頻繁に更新または修正されることがあります。
          <br />
          収支報告書に基づいてレポートを作成していますが、表示内容が正確であることを保証するものではありません。
          <br />
        </Alert.Description>
      </Alert.Content>
    </Alert.Root>
  );
}
