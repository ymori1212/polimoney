# 政治資金収支報告書ダウンロードスクリプト

総務省のウェブサイトから政治資金収支報告書のPDFファイルを自動的にダウンロードするPythonスクリプトです。指定された条件（公表年、団体種別、団体名など）に基づいて対象となる報告書を特定し、効率的かつサーバーに負荷をかけないようにダウンロードします。

## 機能

- 総務省のウェブサイトから政治資金収支報告書のPDFファイルを自動ダウンロード
- 公表年、団体種別、団体名などによるフィルタリング
- 年度ごと、団体種別ごとに整理されたディレクトリ構造でファイルを保存
- ダウンロードしたファイルのメタデータをJSON形式で保存
- プログレスバーによるダウンロード進捗表示
- エラー時の自動リトライ機能
- 並列ダウンロードオプション（デフォルトは無効）
- ドライランモード（実際にダウンロードせずに何が行われるかを表示）
- メタデータのみ収集モード（PDFをダウンロードせず）

## 必要なもの

- Python 3.10以上
- 以下のPythonパッケージ:
  - requests
  - beautifulsoup4
  - tqdm

## インストール

1. リポジトリをクローンまたはスクリプトをダウンロード
2. 必要なパッケージをインストール:

```bash
pip install requests beautifulsoup4 tqdm
```

## 使用方法

基本的な使用方法:

```bash
python download_seijishikin.py
```

これにより、デフォルトの設定で最新の政治資金収支報告書がダウンロードされます。

### オプション

```
-h, --help                ヘルプメッセージを表示
-o, --output-dir DIR      保存先ディレクトリ（デフォルト: downloaded_pdfs）
-y, --year YEAR           公表年（例: R5, R4）、複数指定可能（カンマ区切り）
-c, --category CATEGORY   団体種別（政党本部,政党支部,政治資金団体,その他）、複数指定可能
-n, --name NAME           団体名（部分一致で検索）
-e, --exact-match         団体名の完全一致で検索
-d, --delay SECONDS       リクエスト間の待機時間（秒、デフォルト: 5、最小: 3）
-p, --parallel NUM        並列ダウンロード数（デフォルト: 1）
-f, --force               既存ファイルを上書き
-l, --log-level LEVEL     ログレベル（DEBUG, INFO, WARNING, ERROR、デフォルト: INFO）
-v, --verbose             詳細な出力を表示（--log-level DEBUGと同等）
--dry-run                 実際にダウンロードせずに何が行われるかを表示
--metadata-only           PDFをダウンロードせずメタデータのみ収集
```

### 使用例

1. 令和5年分の政党支部の報告書をダウンロード:

```bash
python download_seijishikin.py -y R5 -c 政党支部
```

2. 「民主党」という名前を含む団体の報告書をダウンロード:

```bash
python download_seijishikin.py -n 民主党
```

3. 令和4年と令和5年の政党本部と政治資金団体の報告書をダウンロード:

```bash
python download_seijishikin.py -y R4,R5 -c 政党本部,政治資金団体
```

4. ドライランモードで何がダウンロードされるかを確認:

```bash
python download_seijishikin.py -n 自民党 --dry-run
```

5. 詳細なログ出力でダウンロード:

```bash
python download_seijishikin.py -v
```

6. 既存ファイルを上書きしてダウンロード:

```bash
python download_seijishikin.py -f
```

7. カスタム出力ディレクトリを指定:

```bash
python download_seijishikin.py -o seijishikin_pdfs
```

## 出力

ダウンロードしたファイルは以下の構造で保存されます:

```
downloaded_pdfs/
├── metadata.json       # ダウンロードしたファイルのメタデータ
├── R5年分/             # 公表年ごとのディレクトリ
│   ├── 政党本部/
│   │   └── *.pdf
│   ├── 政党支部/
│   │   └── *.pdf
│   └── 政治資金団体/
│       └── *.pdf
└── R4年分/
    └── ...
```

### メタデータ形式

`metadata.json` ファイルには以下の情報が含まれます:

```json
{
  "download_date": "2025-05-14T15:30:00+09:00",
  "parameters": {
    "years": ["R5", "R4"],
    "categories": ["政党支部"],
    "name_filter": "民主党",
    "exact_match": false
  },
  "files": [
    {
      "filename": "R5年分/政党支部/国民民主党参議院比例区第2総支部.pdf",
      "original_url": "https://www.soumu.go.jp/senkyo/seiji_s/seijishikin/reports/SS20241129/001810_0021.pdf",
      "organization": "国民民主党参議院比例区第2総支部",
      "category": "政党支部",
      "year": "R5",
      "file_size": 1234567,
      "download_status": "success",
      "download_date": "2025-05-14T15:31:23+09:00"
    },
    // ...
  ],
  "statistics": {
    "total_files": 42,
    "downloaded_files": 40,
    "skipped_files": 2,
    "failed_files": 0,
    "total_size": 123456789
  }
}
```

## 注意事項

- 総務省サーバーへの過度な負荷を避けるため、リクエスト間の待機時間は最低3秒に設定されています。
- 大量のファイルをダウンロードする場合は、`--dry-run` オプションで事前に確認することをお勧めします。
- 並列ダウンロード機能は、サーバーに過度な負荷をかける可能性があるため、デフォルトでは無効になっています。使用する場合は適切な値（2〜3程度）を設定してください。

## ライセンス

このスクリプトはMITライセンスの下で公開されています。詳細はLICENSEファイルを参照してください。

## 貢献

バグ報告や機能リクエストは、Issueトラッカーを通じてお願いします。プルリクエストも歓迎します。