# Architecture

このリポジトリは、TradingAgentsのように役割を分けつつ、最初は堅いルールベースで銘柄候補を出す構成です。

## Agents

- `DataAgent`: データ取得と正規化
- `DividendAgent`: 高配当・安定株スクリーニング
- `GrowthAgent`: 値上がり期待株スクリーニング
- `QualityAgent`: 財務品質の補助評価
- `RiskAgent`: 赤字、CF、配当性向、自己資本比率などのリスク評価
- `ReportAgent`: CSVとMarkdown出力

## Data Source

主データ源はEDINET DB REST APIを想定しています。

EDINET DB MCPはAIエージェントから対話的に財務データを参照する用途に向いています。一方、このリポジトリのようなCLIバッチ処理ではREST APIの方が扱いやすいため、`EdinetDbClient` をREST APIアダプタとして実装しています。

APIキー未設定時、または `--sample` 指定時は、サンプルデータで実行できます。

## Future Work

- EDINET DB REST APIの実レスポンスに合わせた正規化の調整
- 長期株価データの追加
- 配当履歴の長期データ追加
- LLMによる上位候補のコメント生成
- 定期実行ジョブ
