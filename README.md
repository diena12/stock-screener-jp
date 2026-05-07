# stock-screener-jp

UIなしで日本株をスクリーニングするCLIツールです。

高配当・安定株と、値上がり期待株を別ロジックで評価します。TradingAgents風に役割を分けていますが、最初の実装は再現性を優先し、LLMに丸投げせずにルールベースのスコアリングを中心にしています。

## 方針

- 対象は日本株のみ
- 100株で50万円以内の銘柄を優先
- UIは作らず、CSVとMarkdownを出力
- EDINET DB REST APIを主データ源として想定
- API仕様変更に備えてデータ取得層を分離
- 各分析ロールの判断基準は `skills/*/SKILL.md` に明文化

## セットアップ

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -e .
Copy-Item .env.example .env
```

`.env` にEDINET DBのAPIキーを設定してください。

```text
EDINETDB_API_KEY=your_api_key_here
EDINETDB_BASE_URL=https://edinetdb.jp/v1
```

## 実行

```powershell
stock-screen dividend --top 30
stock-screen growth --top 30
stock-screen all --top 30
```

高配当モードは、初期スクリーニング後に上位候補だけを追加レビューします。

```powershell
stock-screen dividend --top 30 --review-top 50
```

レビューではStooqの日足データから最新株価、100株金額、直近約1年の高値安値レンジも取得します。価格取得を止めたい場合:

```powershell
stock-screen dividend --top 30 --review-top 30 --no-price
```

無料API枠を節約したい場合は、レビューをスキップできます。

```powershell
stock-screen dividend --top 30 --no-review
```

## 高配当スコアの考え方

高利回りだけを高評価にはしません。10年以上の長期保有を想定し、以下を重視します。

- 配当継続性
- 減配の少なさ
- 配当額のブレの小ささ
- 株価レンジの小ささ
- 100株購入額が50万円以内か
- 配当性向の無理のなさ
- 自己資本比率、ROE、キャッシュフロー

## 出力

```text
outputs/
  dividend_YYYY-MM-DD.csv
  growth_YYYY-MM-DD.csv
  report_YYYY-MM-DD.md
```

## 投資判断について

このツールは投資助言ではありません。銘柄候補を機械的に整理し、調査対象を絞るための補助ツールです。最終判断は必ず利用者自身で行ってください。
