# Architecture

このリポジトリは、TradingAgentsのように役割を分けつつ、最初は堅いルールベースで銘柄候補を出す構成です。

## Agents

- `DataAgent`: データ取得と正規化
- `DividendAgent`: 高配当・安定株の初期スクリーニング
- `DividendReviewAgent`: 初期候補の上位だけ財務時系列を取得し、配当継続性、配当安定性、株価レンジの安定性を重く見て再評価
- `PriceAgent`: Stooqの日足CSVから最新株価、100株金額、直近約1年の高値安値レンジを取得
- `GrowthAgent`: 値上がり期待株スクリーニング
- `QualityAgent`: 財務品質の補助評価
- `RiskAgent`: 赤字、CF、配当性向、自己資本比率などのリスク評価
- `ReportAgent`: CSVとMarkdown出力

## Dividend Flow

高配当モードは2段階です。

1. EDINET DBのスクリーナーで配当利回り、配当性向、自己資本比率の条件に合う候補を広めに取得する
2. `DividendReviewAgent` が上位候補だけ財務時系列を取り直し、長期保有に向くか再スコアリングする
3. `PriceAgent` が株価を補完し、100株購入額と株価レンジの安定性を評価に加える

再評価では、配当利回りそのものよりも、配当継続性、減配の少なさ、利益の安定性、株価レンジの小ささを重く見ます。

## Data Source

主データ源はEDINET DB REST APIを想定しています。

EDINET DB MCPはAIエージェントから対話的に財務データを参照する用途に向いています。一方、このリポジトリのようなCLIバッチ処理ではREST APIの方が扱いやすいため、`EdinetDbClient` をREST APIアダプタとして実装しています。

APIキー未設定時、または `--sample` 指定時は、サンプルデータで実行できます。
