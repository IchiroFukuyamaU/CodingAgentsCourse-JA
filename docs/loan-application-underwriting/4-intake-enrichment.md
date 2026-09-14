# 申込受付とデータ補完
`uipath-rpa` スキルを使って、CSV から申込者データを読み込み、各ローン申込を UiBank API 経由で送信し、結果を `results.csv` に書き出す Studio の XAML ワークフローを生成します。

## 1. プロジェクトフォルダーをコーディングエージェントで開く

`LoanApplicationDispatcher` という名前の空のフォルダーを作成し、コーディングエージェント（Claude Code、Codex など）で開きます。

```bash
mkdir LoanApplicationDispatcher
```

## 2. 自動化の内容を説明する

作りたいものを、コーディングエージェントに平易な言葉で説明します。

```text
次の処理を行う {YourName}LoanApplicationDispatcher という名前の UiPath Studio の自動化を構築してください:

1. loan-applications.csv を DataTable に読み込む。列は first_name、last_name、email、
   loan_amount、loan_term、yearly_income、age
2. 各行について、UiBank API（https://uibank-api.uipath.com/explorer/swagger.json、
   認証不要）の newquote エンドポイントにローン申込を送信する。Content-Type は
   application/x-www-form-urlencoded の POST リクエストとし、次のようにマッピングする:
   loan_amount → amount、loan_term → term、yearly_income → income、age → age、
   email → email
3. 申込が受理された場合は、{YourName}results.csv に 1 行を書き込む。内容は loan_id
   （レスポンスの quoteid）、ステータス "Loan Submitted"、および申込者の全フィールド。
   そのうえで、CodingAgentsILT フォルダー内のフロープロセス {YourName}LoanUnderwritingProcess を
   開始し、loan_id、applicant_first_name、applicant_last_name、loan_amount、loan_term、
   income を入力として渡す。プロセスが完了したら、final_decision に基づいて
   {YourName}results.csv のステータスを "Loan Approved" または "Loan Rejected" に更新する
4. 申込が却下された場合は、loan_id を空、ステータスを "Failed"、エラーを
   "Application rejected" として {YourName}results.csv に 1 行を書き込む
5. 各行の処理を Try/Catch で囲む。例外が発生した場合は、loan_id を空、ステータスを
   "Failed"、例外メッセージをエラーとして {YourName}results.csv に 1 行を書き込む
6. すべての行の処理が終わったら、{YourName}results.csv を Orchestrator の
   CodingAgentsILT フォルダー内の LoanUnderwriting ストレージバケットにアップロードする

このプロジェクトはクロスプラットフォーム（Windows 用ではなく）として作成してください。
生成するのはプロジェクトファイルのみで構いません。
```

コーディングエージェントは `uipath-rpa` スキルのコンテキストを読み取り、完全な Studio プロジェクトを生成します。

- `Main.xaml` — API 認証、ForEach ループ、HTTP リクエスト、CSV 出力を含むメインのワークフロー
- `project.json` — プロジェクト設定とアクティビティパッケージの依存関係

## 3. 生成されたワークフローをレビューする

Studio で `Main.xaml` を開きます。次の内容が確認できるはずです。

- **Read CSV** — `loan-applications.csv` を DataTable に読み込む
- **For Each Row in Data Table** — 申込者ごとにループする
  - **HTTP Request** — `/api/quotes/newquote` に対して、フォームエンコードされたフィールド（amount、term、income、age、email）で POST する
  - **Deserialize JSON** — レスポンスを解析して `accepted` と `quoteid` を取り出す
  - **If** — `accepted` で分岐する
  - **Append Line / Write CSV** — 結果の行を `results.csv` に追記する
- **Try/Catch** — 各行を囲み、失敗しても実行全体が止まらないようにする

!!! note "Start Job のエントリーポイントを確認してください"
    `{YourName}LoanUnderwritingProcess` を起動する **Start Job** アクティビティを探し、プロセス名とフォルダーパスが正しく設定されているか確認してください。レッスン 3 でデプロイした内容と完全に一致している必要があります。エントリーポイントのパスが誤っていると、ジョブの開始に失敗します。

HTTP Request アクティビティがフォームのボディを正しく設定していない場合は、コーディングエージェントに修正を依頼します。

```text
/api/quotes/newquote への HTTP Request は、JSON ボディではなく、Content-Type
application/x-www-form-urlencoded のフォームフィールドを使う必要があります。
アクティビティを修正してください。
```

## 4. 実行する前に

`loan-applications.csv` がプロジェクトフォルダーにあることを確認してください。まだ作成していない場合は、次のサンプルデータを使ってコーディングエージェントに生成してもらえます。

```text
次のデータを使って、カレントフォルダーに loan-applications.csv というファイルを作成してください:

first_name,last_name,email,loan_amount,loan_term,yearly_income,age
Alice,Nguyen,alice.nguyen@example.com,15000,3,48000,34
Ben,Carter,ben.carter@example.com,50000,5,30000,40
Clara,Osei,clara.osei@example.com,70000,5,28000,29

各行の first_name、last_name、email は、上記とは異なる値に置き換えてください。
自分の名前を使っても、架空の値を作っても構いませんが、上記と同じにはしないでください。
loan_amount、loan_term、yearly_income、age は変更せずそのまま残してください。
```

## 5. 実行してテストする

Studio でプロジェクトを開き、`Main.xaml` を実行します。ワークフローが認証を行い、各申込を API 経由で送信していく様子を Output パネルで確認してください。そのうえで、次を検証します。

- **`results.csv`** — ファイルを開き、3 行が出力されていること、各行に `loan_id` があり、ステータスが `Loan Approved` または `Loan Rejected` になっていることを確認します

## 6. Orchestrator に公開する

=== "手動で行う場合"

    まず、プロジェクトフォルダーの *中ではなく* **隣** に `Package` フォルダーを作成します。`<working-folder>` は `{YourName}LoanApplicationDispatcher` を含む親フォルダーに置き換えてください。

    ```bash
    mkdir "<working-folder>\Package"
    ```

    フォルダー構成は次のようになります。

    ```text
    <working-folder>\
        {YourName}LoanApplicationDispatcher\   ← Studio のプロジェクト
        Package\                    ← .nupkg の保存先
    ```

    続いて、プロジェクトを `.nupkg` ファイルにパックします。

    ```bash
    uip rpa pack "<working-folder>\{YourName}LoanApplicationDispatcher" "<working-folder>\Package"
    ```

    パックされた `.nupkg` ファイルが `Package` フォルダー内に生成されます。これを Orchestrator にアップロードします。

    ```bash
    uip or packages upload "<working-folder>\Package\{YourName}LoanApplicationDispatcher.1.0.0.nupkg"
    ```

    そのうえで、アップロードしたパッケージからプロセスを作成します。

    ```bash
    uip or processes create --folder-path "CodingAgentsILT" --name "{YourName}LoanApplicationDispatcher" --package-key {YourName}LoanApplicationDispatcher --package-version 1.0.0
    ```

=== "コーディングエージェントに任せる場合"

    次のプロンプトをコーディングエージェントに渡してください。パック、アップロード、プロセスの作成までを代行してくれます。

    ```text
    いま構築した {YourName}LoanApplicationDispatcher の Studio 自動化を公開し、
    Orchestrator のプロセスを作成してください。

    1. プロジェクトを .nupkg にパックしてください（プロジェクトの中ではなく、隣に置いた
       Package フォルダーを使用すること）。
    2. 生成されたパッケージを Orchestrator にアップロードしてください。
    3. そのパッケージから、CodingAgentsILT フォルダー内に、プロジェクトと同じ名前で
       プロセスを作成してください。
    4. プロセスキーを報告してください。
    ```

## 7. ローン審査をエンドツーエンドで実行する

**Orchestrator** で **CodingAgentsILT** フォルダーを開き、`{YourName}LoanApplicationDispatcher` を選択して、手動で実行を開始します。

`loan-applications.csv` の各申込が送信され、受理されたものについて Maestro フローが開始され、結果が返ってくる様子を確認してください。中リスク・高リスクの申込については、**Action Center** を開いて人的レビューのタスクを完了させます。実行が完了したら `results.csv` を開き、すべての行の最終ステータスが Loan Approved または Loan Rejected になっていることを確認してください。
