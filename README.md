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
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
```

`.env` にEDINET DBのAPIキーを設定してください。

```text
EDINETDB_API_KEY=your_api_key_here
```

## 実行

```powershell
stock-screen dividend --top 30
stock-screen growth --top 30
stock-screen all --top 30
```

開発中にパッケージインストール前の状態で動かす場合:

```powershell
python -m stock_screener.cli dividend --top 30
```

## 出力

```text
outputs/
  dividend_YYYY-MM-DD.csv
  growth_YYYY-MM-DD.csv
  report_YYYY-MM-DD.md
```

## 現在の制約

EDINET DBはMCPとREST APIの両方がありますが、このCLIでは定期実行・バッチ処理に向いたREST API利用を想定しています。

ただし、EDINET DBのREST APIレスポンス形状は運用中に調整される可能性があるため、まずは `src/stock_screener/data/edinetdb_client.py` の正規化処理を差し替えやすくしています。

10年以上保有向けの判断を目指しますが、EDINET DBの記事情報ではカバレッジ期間はFY2020-FY2025です。最初は6年程度の財務安定性を評価し、将来的に長期株価・配当履歴データを追加して補完します。

## 投資判断について

このツールは投資助言ではありません。銘柄候補を機械的に整理し、調査対象を絞るための補助ツールです。最終判断は必ず利用者自身で行ってください。
