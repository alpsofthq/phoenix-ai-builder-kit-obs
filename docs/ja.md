# Phoenix AI Builder Kit · OBA RUN Season 2

[한국어](../README.md) · [English](en.md)

**2026年11月7日**のOBAハッカソン参加者向けガイドと実行サンプルです。アカウント・キー・使用量は[開発者ポータル](https://openapi.chickstockfi.com/ja/login)で管理します。[APIリファレンス](https://openapi.chickstockfi.com/ja/docs)にはBuilder対象外の機能も含まれます。

## 接続と利用枠

| 項目 | 内容 |
| --- | --- |
| REST Base URL | `https://api.chickstockfi.com/openapi/v1` |
| DATA MCP | `https://api.chickstockfi.com/openapi/v1/mcp` |
| 認証 | `Authorization: Bearer YOUR_TEAM_KEY`（`ck_live_…`） |
| キー | 主催者の申請コードとメール認証でチーム別アカウントを申請。有効なDATAキーは最大2個 |
| 事前テスト | 有効化後〜**2026-11-07 00:00 KST未満**：累計**1,000回・10 RPM** |
| 本イベント | **2026-11-07 00:00以上〜2026-11-08 00:00 KST未満**：累計**10,000回・20 RPM** |
| 同時リクエスト | チームごとに最大2件。イベント全体の混雑制限も適用 |

KSTはUTC+09:00で、日本時間と同じです。全キー・REST・MCP・APIドキュメントの試行はチームの利用枠を共有します。事前テスト分は本イベントの枠から差し引きません。キーの交換や日付変更では段階内の累計枠は回復しません。期間終了後はデータ取得が停止し、Freeプランへの移行はありません。

`GET /key`とMCP初期化・ツール一覧はDATA取得総量を消費しませんが、別途速度制限があります。処理を受け付けたリクエストは400・404でも計上される場合があります。使用量はポータルまたは`/key`で確認してください。

## 提供範囲

韓国株価・日次価格、韓国/米国の財務・指標・売上構成・配当・開示由来のガイダンス、スクリーナー・セクター情報、韓国開示一覧/原文、米国開示一覧、**公開済みの韓国/米国AI開示分析**、米国決算予定、韓国IR/IPO予定、対応する経済/企業イベントを利用できます。

スクリーナー・セクター出力に含まれる価格・時価総額・評価指標は利用可能です。**米国/日本株価の直接取得・価格履歴・ストリーミングは対象外**です。日本市場データ、ニュース/ニュースワイヤー、外部コンセンサス/アナリスト調査、PRO/ニュースルーム、新規AI生成/翻訳、**Webhook全般**も提供しません。PRO MCPやOAuthは使用せず、DATA MCPとDATAキーを使います。

`POST /query`はリクエストごとに**クエリ1件**です。

```json
{"queries":[{"dataset":"screener","market":"US","limit":3}]}
```

`GET /disclosures`には韓国の`symbol`が必要です。米国開示は`/us-filings`、**米国**決算予定は`/earnings`です。`/symbols`は韓国銘柄検索です。公開済み分析は`/disclosures/{id}/analysis`で取得します。IDは14桁のDART受付番号または`TICKER:ACCESSION`をURLエンコードして指定します。分析がない場合は`404 ANALYSIS_NOT_AVAILABLE`となり、新規生成は行いません。米国一覧では`analysis=published`で公開分析のある開示を絞り込めます。

## 実行例

チーム代表者1名が [Builder 申請](https://openapi.chickstockfi.com/ja/request?product=builder)で主催者から受け取ったコードを入力し、メール認証後にパスワードを設定してください。ログイン後、DATA キーを作成します。発行済みアカウントは引き続き使用できます。申請コードは API キーではありません。公開リポジトリに保存しないでください。認証コードは10分間有効で、5回の誤入力でロックされます。再申請でパスワードや利用枠はリセットされません。既存の有料・PoC アカウントや重複チームは担当者が確認します。

Node.js 22以上またはPython 3.11以上を使用します。追加パッケージは不要です。

```sh
git clone https://github.com/alpsofthq/phoenix-ai-builder-kit-obs.git
cd phoenix-ai-builder-kit-obs
cp .env.example .env
# .envのYOUR_TEAM_KEYを自分のキーに置き換えてから実行します。
set -a
. ./.env
set +a
node examples/javascript/quickstart.mjs usage
python3 examples/python/quickstart.py disclosures 005930
```

PowerShellでは`$env:PHOENIX_DATA_KEY = 'YOUR_TEAM_KEY'`を設定します。他のコマンドは`quote 005930`、`financials AAPL`、`us-filings AAPL`、`screener US`、`earnings`、`analysis FILING_ID`です。実行1回につき1リクエスト、タイムアウト20秒、自動再試行なしです。キーはサーバーかローカルCLIで管理し、ブラウザの公開バンドルに入れないでください。

## MCP

[Claude Code設定](../config/claude.mcp.json.example)を`.mcp.json`に、または[Cursor設定](../config/cursor.mcp.json.example)を`.cursor/mcp.json`に追加します。既存ファイルは上書きせず項目を統合してください。アプリの実行環境に`PHOENIX_DATA_KEY`を設定します。Claudeは`${PHOENIX_DATA_KEY}`、Cursorは`${env:PHOENIX_DATA_KEY}`を使います。リモートMCPはこのリポジトリの`.env`を自動では読み込みません。[Claude公式文書](https://code.claude.com/docs/en/mcp#environment-variable-expansion-in-mcpjson)・[Cursor公式文書](https://cursor.com/docs/mcp#config-interpolation)を参照してください。

最初に「get_api_usageで対象市場、残り回数、終了日時を確認してください」と依頼します。次に「list_disclosuresにsymbol=005930、limit=2を指定してください。新規分析は生成しないでください」と試してください。利用可能なツールと引数は`tools/list`に表示されます。HTTP 200でもJSON-RPCの`error`や`isError: true`なら成功ではありません。

## エラー・公開・問い合わせ

- 429は`Retry-After`を守り、503は間隔を広げながら回数を限定して再試行します。入力不備・権限拒否・分析なし・総量超過・期限終了は自動再試行しません。
- `BUILDER_SCOPE_DENIED`は対象外、`BUILDER_SINGLE_QUERY`はクエリ数超過、`BUILDER_ENDED`は期間終了です。クエリの`results[].ok`も確認してください。
- 日付・単位・通貨・出典・`meta.as_of`を表示し、欠損値を0に置き換えないでください。次ページが必要なときだけ同じ条件に`next_cursor`を指定します。
- 許可されたデータをイベント作品の外部LLM入力・MCP結果として利用できます。Phoenix AIサーバー上の新規AI生成は対象外です。
- コードと画面デモは公開可能です。出典を**Phoenix AI**と表示してください。キー・パスワード・セッション・全レスポンス・データダンプ・再配布用データセットは公開しないでください。
- イベント後の継続運用・データ再配布は別途相談が必要です。例示コードの公開とAPIデータの利用権は別です。[利用規約](https://openapi.chickstockfi.com/ja/terms)も適用されます。

一般的な連携質問は[Issues](https://github.com/alpsofthq/phoenix-ai-builder-kit-obs/issues)、アカウント・非公開事項・継続利用は[お問い合わせ](https://openapi.chickstockfi.com/ja/request)またはhelp@alpsoft.ioへ。発生日時・経路・HTTP状態・エラーコード・リクエストIDを記載し、認証情報や全レスポンスは送らないでください。

確認日：2026-11-04 · DATA API仕様1.18.0
