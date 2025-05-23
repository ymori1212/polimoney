# Polimoney

Polimoney は[デジタル民主主義2030](https://dd2030.org/)の一環として、政治資金の透明性を高めるために開発されたオープンソースのプロジェクトです。政治資金収支報告書のデータを視覚化し、市民が政治資金の流れを容易に理解できるようにすることを目指しています。

## 技術スタック

### フロントエンド

- **Next.js**
- **TypeScript**

```
npm install --legacy-peer-deps
npm run dev
```

### データ処理ツール

- **Python**
  - **pdf2image**
  - **Google Gemini AI**

詳細は`tools/README.md`を参照してください。

### converter

OCR処理で作成したJSONをウェブフロントエンド用のデータ構造に変換します。

```bash
# 実行例
npx tsx data/converter.ts -i data/sample_input.json -o data/sample_output.json
# エラーを無視してJSONを出力
npx tsx data/converter.ts --ignore-errors -i data/sample_input.json -o data/sample_output.json
```


## 貢献ガイドライン

このプロジェクトはオープンソース(APGLライセンス)であり、誰でも貢献することができます。
詳細は以下のドキュメントを参照してください。
- [CONRIBUTING](CONTRIBUTING.md)
- [LICENSE](LICENSE)
- [CLA](CLA.md)
- [PROJECTS](PROJECTS.md)
- [CODE_REVIEW_GUIDELINES](CODE_REVIEW_GUIDELINES.md)
- [DEVIN_COLLABORATION](DEVIN_COLLABORATION.md)
- [ADR](docs/adr/ADR.md)
