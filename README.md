# Polimoney

Polimoney は、デジタル民主主義2030プロジェクトの一環として、政治資金の透明性を高めるために開発されたオープンソースのプロジェクトです。政治資金収支報告書のデータを視覚化し、市民が政治資金の流れを容易に理解できるようにすることを目指しています。

## 特徴

- **データの視覚化**: サンキー図を使用して収入と支出の流れを視覚的に表現
- **詳細な取引情報**: 収入・支出の詳細な取引データを表形式で表示
- **政治家プロフィール**: 政治家の基本情報と所属政党などを表示
- **メタデータ表示**: 政治団体の詳細情報を表示

## 技術スタック

### フロントエンド
- **Next.js 15.2.4** - Reactフレームワーク（App Routerを使用）
- **React 19.1.0** - UIライブラリ
- **TypeScript** - 型安全な開発言語
- **Chakra UI** - UIコンポーネントライブラリ
- **Nivo** - データ可視化ライブラリ（サンキー図など）

### データ処理ツール
- **Python** - PDF処理と画像分析
  - **pdf2image** - PDF→画像変換
  - **Google Gemini AI** - 画像分析（OCRと構造化）

## プロジェクト構造

```
polimoney/
├── app/ - Next.js App Router
│   ├── page.tsx - トップページ（政治家一覧）
│   ├── [slug]/page.tsx - 詳細ページ（個別の政治家データ）
│   └── ...
├── components/ - Reactコンポーネント
│   ├── BoardChart.tsx - サンキー図表示
│   ├── BoardContainer.tsx - ボードのコンテナ
│   └── ...
├── data/ - データファイル
│   ├── demo-*.ts - デモデータ
│   └── ...
├── public/ - 静的ファイル
├── tools/ - データ処理ツール
│   ├── pdf_to_images.py - PDF→画像変換ツール
│   └── ...
└── todo.md - 改善計画
```

## セットアップと実行方法

### 必要条件
- Node.js 18.0.0以上
- npm または yarn
- Python 3.8以上（データ処理ツール使用時）

### インストール

```bash
# リポジトリのクローン
git clone https://github.com/your-username/polimoney.git
cd polimoney

# 依存パッケージのインストール
npm install

# Pythonツール用の依存パッケージインストール（オプション）
cd tools
pip install -r requirements.txt
cd ..
```

### 開発サーバーの起動

```bash
npm run dev
```

ブラウザで [http://localhost:3000](http://localhost:3000) を開いてアプリケーションにアクセスできます。

### ビルドと本番環境での実行

```bash
npm run build
npm run start
```

## データ処理ツールの使用方法

### PDFから画像への変換

```bash
cd tools
python pdf_to_images.py path/to/your/pdf_file.pdf
```

変換された画像は `tools/output_images` ディレクトリに保存されます。

## 貢献ガイドライン

todo

## **ライセンス**

todo

## 連絡先

質問や提案がある場合は、Issueを作成するか、プロジェクト管理者にお問い合わせください。
