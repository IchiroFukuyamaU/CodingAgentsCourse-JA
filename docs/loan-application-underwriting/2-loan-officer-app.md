# ローン担当者レビュー用ダッシュボード
`uipath-coded-apps` スキルを使って、Maestro の人的タスク（Human Task）のレビュー画面内でレンダリングされる React 製の Coded Action App を生成します。AI による与信審査の結果を表示し、ローン担当者が申込を承認または却下できるようにします。

## 1. プロジェクトフォルダーをコーディングエージェントで開く

`{yourname}loanofficerdashboard` という名前の空のフォルダーを作成し、コーディングエージェント（Claude Code、Codex など）で開きます。

```bash
mkdir {yourname}loanofficerdashboard
```

## 2. アプリの内容を説明する

作りたいものを、コーディングエージェントに平易な言葉で説明します。担当者に何が見えるのか、データはどこから来るのか、判断ボタンが何をするのかを具体的に伝えてください。

```text
UiPath TypeScript SDK を使って、{yourname}loanofficerdashboardApp という名前の
Coded Action App を構築してください。要件は次のとおりです:

1. 12 個の入力を受け取る: LoanId（string）、ApplicantFirstName（string）、
   ApplicantLastName（string）、LoanAmount（number）、LoanTerm（number）、
   YearlyIncome（number）— これらは Maestro プロセスから渡されます — に加えて、
   コーデッドエージェントの 6 つの出力: CreditScore（number、0〜100）、RiskBand
   （string — Low / Medium / High）、AssessmentSummary（string）、
   MonthlyRepayment（number）、DebtToIncomeRatio（number）、
   LoanToMarketRatio（number）
2. 2 ペイン構成のダッシュボードを表示する: 左ペインには申込者名、LoanId、
   借入額、借入期間、年収を表示し、右ペインには CreditScore をプログレスバーで、
   RiskBand を色分けしたバッジで（緑 = Low、黄 = Medium、赤 = High）、
   AssessmentSummary をテキストブロックで、さらに 3 つの財務指標
   （月々の返済額、債務所得比率、市場平均に対する借入額の比率）を
   ラベル付きの値として表示する
3. ローン担当者がコメントを追加できる、任意入力の Notes テキストエリアを用意する
4. ローン担当者が Approve（緑）または Reject（赤）のボタンで判断を送信できるようにする。
   これらは action-schema.json の outcomes として定義し、外部 API の呼び出しは不要とする
```

コーディングエージェントは `uipath-coded-apps` スキルのコンテキストを読み取り、完全なアプリプロジェクトを生成します。

- `src/App.tsx` — 2 ペインレイアウトを持つメインの React コンポーネント
- `action-schema.json` — すべての入力と `Approve` / `Reject` の outcomes を定義
- `package.json` — プロジェクトの依存関係
- `vite.config.ts` — `base: './'` を設定した Vite の設定ファイル

## 3. 生成されたコードをレビューする

プロジェクトを IDE で開きます。次の内容が確認できるはずです。

- **`action-schema.json`** — `inputs` セクションに `LoanId`、`CreditScore`、`RiskBand`、`AssessmentSummary` があり、`outcomes` セクションに `Approve` と `Reject` がある
- **`App.tsx`** — 2 ペインレイアウト、クレジットスコアのプログレスバー、色分けされたリスクバッジ。入力はアクションスキーマのコンテキストから直接読み取られている

## 4. ローカルで実行する

!!! note
    以下のコマンドはアプリのフォルダー内で実行してください。まず移動します。
    ```bash
    cd LoanOfficerDashboard
    ```

```bash
npm install
npm run dev
```

サーバーが正常に起動すると、次のように表示されます。

```text
  VITE v8.0.16  ready in 308 ms

  ➜  Local:   http://localhost:5174/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

`http://localhost:5174/` を直接開くと、データのない状態のレイアウトが表示されます。パラメーターが渡されていないため、各フィールドは空です。ポート番号は環境によって異なります（5173、5174 など）。ターミナルに表示された番号を使ってください。

### ワークショップ用プロンプト — デモモード

Action Center に依存せず、操作可能なボタン付きでもう少しリッチにローカルプレビューしたい場合は、コーディングエージェントに次のように依頼します。

```text
Coded Action App のローカルテスト版を起動し、現実的なダミーデータでインターフェイスを
プレビューできるクリック可能な URL を教えてください。

次の条件を満たす安全なデモモードを追加してください:

- localhost でのみ動作し、Action Center のタスクを必要としない
- action-schema.json に定義されたすべての入力に値を設定する
- Notes、テーマ切り替え、outcome のボタンは操作可能なままにする
- UiPath の API を呼び出したり、実際のタスクを完了させたりしない
- 通常の本番時の挙動は一切変更しない

アプリを再ビルドして lint を実行し、ローカル開発サーバーを起動して、その URL が HTTP 200 を
返すことを確認したうえで、クリック可能なデモ URL を教えてください。
```

## 5. ビルド・パック・パブリッシュ

```bash
npm run build
uip codedapp pack dist -n {yourname}loanofficerdashboard --version 1.0.0
uip codedapp publish -t Action
```

`-t Action` フラグは必須です。これによってアプリが Coded Action App として登録され、Maestro が人的タスクをこのアプリに振り向けられるようになります。

## 6. Orchestrator にデプロイする

```bash
uip codedapp deploy -n {yourname}loanofficerdashboard --folder-key <CodingAgentsILT-folder-key>
```

例:

```bash
uip codedapp deploy -n {yourname}loanofficerdashboard --folder-key c30345cd-5543-46a9-b42b-0354e60b4f15
```

CodingAgentsILT のフォルダーキーを調べるには、次を実行します。

```bash
uip or folders list --output json
```

`Name` が `CodingAgentsILT` のエントリーを探し、その `Key` の値をコピーしてください。

これでアプリが有効になりました。レッスン 3 では、Maestro が人的レビューのステップで一時停止し、ローン担当者が入力できるようにこのアプリをレンダリングします。

### デプロイを確認する

**Orchestrator** で **CodingAgentsILT** フォルダー → **Apps** を開き、`{yourname}loanofficerdashboard` が正常にデプロイされて表示されていることを確認してください。
