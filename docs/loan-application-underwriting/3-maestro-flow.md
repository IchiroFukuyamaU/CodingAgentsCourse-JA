# Maestro Flow によるオーケストレーション
`uipath-maestro-flow` スキルを使って、コーデッドエージェントとローン担当者用ダッシュボードをつなぎ、リスクバンドに応じて申込を振り分ける UiPath Flow プロセスを生成します。

## 1. プロジェクトフォルダーをコーディングエージェントで開く

`{YourName}LoanUnderwritingProcess` という名前の空のフォルダーを作成し、コーディングエージェント（Claude Code、Codex など）で開きます。

```bash
mkdir {YourName}LoanUnderwritingProcess
```

## 2. プロセスの内容を説明する

フロー全体を、コーディングエージェントに平易な言葉で説明します。

```text
uipath-maestro-flow スキルを使って、{YourName}LoanUnderwritingProcess という名前の
UiPath Flow プロセスを構築してください。要件は次のとおりです:

1. 6 つの入力を受け取る: loan_id、applicant_first_name、applicant_last_name、
   loan_amount、loan_term、income
2. エージェント {YourName}LoanUnderwritingAgent（CodingAgentsILT フォルダー内）を
   呼び出し、loan_id を渡して、返された値をプロセス変数として保持する:
   credit_score、risk_band、assessment_summary、monthly_repayment、
   debt_to_income_ratio、loan_to_market_ratio
3. risk_band が "Low" の場合は申込を自動承認してプロセスを終了する
4. Medium または High の場合は、アプリ {yourname}loanofficerdashboard
   （CodingAgentsILT フォルダー内）を開き、12 個の入力すべて（LoanId、
   ApplicantFirstName、ApplicantLastName、LoanAmount、LoanTerm、YearlyIncome、
   CreditScore、RiskBand、AssessmentSummary、MonthlyRepayment、
   DebtToIncomeRatio、LoanToMarketRatio）を渡し、officer_decision を受け取る
5. officer_decision に基づいて Approved または Rejected で終了する
6. 自動承認された場合もローン担当者が判断した場合も、いずれのケースでも
   final_decision（string — "Approved" または "Rejected"）を出力する
```

コーディングエージェントは `uipath-maestro-flow` スキルのコンテキストを読み取り、完全なプロジェクトを生成します。

- `{YourName}LoanUnderwritingProcess.flow` — すべてのノード、エッジ、変数マッピングを含むフロー定義
- `project.uiproj` — プロジェクトマニフェスト

## 3. 生成されたフローをレビューする

`{YourName}LoanUnderwritingProcess.flow` をテキストエディタで開くか、コーディングエージェントに構造を説明させてください。次の内容が確認できるはずです。

- 6 つのプロセス入力変数（`loan_id`、`applicant_first_name`、`applicant_last_name`、`loan_amount`、`loan_term`、`income`）を持つ **Start ノード**
- `loan_id` を入力として `{YourName}LoanUnderwritingAgent` を呼び出し、6 つの出力変数（`credit_score`、`risk_band`、`assessment_summary`、`monthly_repayment`、`debt_to_income_ratio`、`loan_to_market_ratio`）を受け取る **Agent ノード**
- `risk_band == "Low"` で分岐する **Condition ノード**
- `{yourname}loanofficerdashboard` に接続され、12 個の変数（`LoanId`、`ApplicantFirstName`、`ApplicantLastName`、`LoanAmount`、`LoanTerm`、`YearlyIncome`、`CreditScore`、`RiskBand`、`AssessmentSummary`、`MonthlyRepayment`、`DebtToIncomeRatio`、`LoanToMarketRatio`）がすべて入力としてマッピングされ、`officer_decision` を出力とする **Human Task ノード**
- `officer_decision == "Approve"` で分岐する 2 つ目の **Condition ノード**
- 3 つの **End ノード**（Auto-Approved、Approved、Rejected）

マッピングや条件の調整が必要な場合は、コーディングエージェントに次のように依頼します。

```text
リスクバンドの条件を修正して、既定の経路が人的レビューのノードに向かい、明示的な条件分岐のほうで
"Low" の自動承認ケースを処理するようにしてください。
```

!!! tip "Studio Web でフローを可視化する"
    生成された `.flow` ファイルは **Studio Web** にインポートでき、Orchestrator にデプロイする前にプロセスの図を確認したり、対話的にテストしたりできます。**Studio Web** を開いて新しい Flow プロジェクトを作成し、`{YourName}LoanUnderwritingProcess.flow` をインポートしてください。コーディングエージェントが生成したとおりのノード、条件、接続がキャンバスに描画されます。

## 4. 生成されたフローをテストする

UiBank から検証済みのローンレコードを取得し、フロー用の有効なテスト入力を生成するよう、コーディングエージェントに依頼します。

```text
UiBank の Swagger ドキュメントを開いて内容を確認してください:

https://uibank-api.uipath.com/explorer/swagger.json

API に記載されているエンドポイントのみを使い、ローン見積を取得するための読み取り専用エンドポイントを
特定してください。GET リクエストを実行し、現在 UiBank に存在するローン見積を 1 件選んでください。

検証済みのローンレコードを使って、{YourName}LoanUnderwritingProcess フロー用のテスト入力を
生成してください。

要件:
- Swagger 仕様に記載された GET エンドポイントのみを使用すること。
- データの作成・更新・削除は一切行わないこと。
- loan_id を捏造したり、存在を確認していない ID を使い回したりしないこと。
- 選んだローンレコードが実在することを検証すること。
- loan_amount、loan_term、income は同一の検証済みレコードから設定すること。
- loan_term は年数を表し、1、3、5、10 のいずれかでなければならない。
- レコードの年収を income にマッピングすること。
- 申込者名はレコードにあればそれを使用すること。API が申込者名を提供しない場合は、
  ワークショップ用の安全な値として John と Doe を使用すること。
- 有効な JSON オブジェクトをちょうど 1 つだけ返すこと。
- Markdown、説明、コメント、PowerShell コマンドは含めないこと。

必須の出力形式:

{
  "loan_id": "<VERIFIED_LOAN_ID>",
  "applicant_first_name": "<FIRST_NAME>",
  "applicant_last_name": "<LAST_NAME>",
  "loan_amount": <LOAN_AMOUNT>,
  "loan_term": <1_OR_3_OR_5_OR_10>,
  "income": <YEARLY_INCOME>
}
```

コーディングエージェントは次のような結果を返すはずです。

```json
{
  "loan_id": "6a4203a1f4865600481c657b",
  "applicant_first_name": "John",
  "applicant_last_name": "Doe",
  "loan_amount": 15000,
  "loan_term": 3,
  "income": 48000
}
```

## 5. 検証とパック

=== "手動で行う場合"

    生成された `.flow` ファイルの親フォルダーに移動します。

    ```bash
    cd "parent-folder-path/to/{YourName}LoanUnderwritingProcess"
    ```

    パスは、お使いのマシン上の実際の場所に置き換えてください。

    パックする前に、フローを検証します。

    ```bash
    uip maestro flow validate {YourName}LoanUnderwritingProcess.flow
    ```

    command not found エラーが出る場合は、maestro ツールが未インストールか、PATH に入っていない可能性があります。

    ```bash
    # 1. maestro-tool をインストールする（初回のみ）
    npm install -g @uipath/maestro-tool --prefix "$HOME/.npm-global"

    # 2. PATH に追加する（新しいターミナルごとに必要。~/.zshrc に書けば恒久的）
    export PATH="$HOME/.npm-global/bin:$PATH"

    # 毎回手順 2 を実行しなくて済むよう、次を一度だけ実行しておく:
    echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.zshrc

    # 3. 検証する
    uip maestro flow validate {YourName}LoanUnderwritingProcess.flow
    ```

    警告があれば修正し、そのうえでパックします。

    ```bash
    uip maestro flow pack "<path-to-your-flow-folder>/{YourName}LoanUnderwritingProcess" /tmp/dist --version 1.0.0 --output json
    ```

    例:

    ```bash
    uip maestro flow pack "/path/to/{YourName}LoanUnderwritingProcess/{YourName}LoanUnderwritingProcess" /tmp/dist --version 1.0.0 --output json
    ```

    パッケージを Orchestrator にアップロードし、`CodingAgentsILT` フォルダーにプロセスを作成します。

    ```bash
    uip or packages upload /tmp/dist/{YourName}LoanUnderwritingProcess.flow.Flow.1.0.0.nupkg --output json
    ```

    例:

    ```bash
    uip or packages upload /tmp/dist/MadalinaLoanUnderwritingProcess.flow.Flow.1.0.0.nupkg --output json
    ```

    command not found エラーが出る場合は、maestro ツールが未インストールか、PATH に入っていない可能性があります。

    ```bash
    # 1. maestro-tool をインストールする（初回のみ）
    npm install -g @uipath/maestro-tool --prefix "$HOME/.npm-global"

    # 2. PATH に追加する（新しいターミナルごとに必要。~/.zshrc に書けば恒久的）
    export PATH="$HOME/.npm-global/bin:$PATH"

    # 毎回手順 2 を実行しなくて済むよう、次を一度だけ実行しておく:
    echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.zshrc

    # 3. アップロードを再実行する
    uip or packages upload /tmp/dist/{YourName}LoanUnderwritingProcess.flow.Flow.1.0.0.nupkg --output json
    ```

    そのうえでプロセスを作成します。

    ```bash
    uip or processes create --name "{YourName}LoanUnderwritingProcess" --package-key "{YourName}LoanUnderwritingProcess.flow.Flow" --package-version "1.0.0" --folder-key "c30345cd-5543-46a9-b42b-0354e60b4f15" --output json
    ```

    例:

    ```bash
    uip or processes create --name "MadalinaLoanUnderwritingProcess" --package-key "MadalinaLoanUnderwritingProcess.flow.Flow" --package-version "1.0.0" --folder-key "c30345cd-5543-46a9-b42b-0354e60b4f15" --output json
    ```

=== "コーディングエージェントに任せる場合"

    次のプロンプトをコーディングエージェントに渡してください。検証・公開・デプロイまでを代行してくれます。

    ```text
    いま構築した {YourName}LoanUnderwritingProcess の Maestro フローを公開してデプロイしてください。

    1. 生成された .flow ファイルを見つけて検証し、報告された警告があれば修正してください。
    2. Orchestrator の CodingAgentsILT フォルダー
       （folder-key c30345cd-5543-46a9-b42b-0354e60b4f15）に、バージョン 1.0.0 として公開してください。
    3. 同じフォルダー内で、公開したパッケージからプロセスを作成してデプロイしてください。
    4. プロセスキーを報告してください。
    ```

## 6. フロー全体をテストする

Orchestrator からプロセスを 3 回起動します。下記の申込者ごとに 1 回ずつです。各 `loan_id` は UiBank に実在する検証済みのレコードです（エージェントはこのレコードを再取得してスコアリングするため、下記の金額・期間・収入はレコードの内容と一致しています）。

```json
{"loan_id": "6a8dabd21feca3004834197a", "applicant_first_name": "Alice", "applicant_last_name": "Nguyen", "loan_amount": 25001, "loan_term": 3, "income": 80000}
```

```json
{"loan_id": "6a8c0bb11feca300483416cb", "applicant_first_name": "Ben", "applicant_last_name": "Carter", "loan_amount": 120000, "loan_term": 10, "income": 30000}
```

```json
{"loan_id": "6a8db0e11feca30048341981", "applicant_first_name": "Clara", "applicant_last_name": "Osei", "loan_amount": 12000, "loan_term": 10, "income": 1200}
```

これらの ID は共有の UiBank サンドボックス上の実データを指しており、本レッスン作成時点で実在が確認されています。また、債務所得比率によって各バンドがはっきり分かれるように選ばれています（Alice 約 10%（Low）、Ben 約 40%（Medium）、Clara 約 100%（High））。UiBank のデータがリセットされた場合は、手順 4 の Swagger による検索を使って、同様に差がはっきり出る新しいレコードを 3 件探してください。スコアリングは LLM によるものなので、新しいレコードを使う前には必ず再実行して、得られた `risk_band` を確認してください。

| 申込者 | 想定される経路 |
|---|---|
| Alice — 少額のローン、十分な収入 | 低リスク → 自動承認、人的タスクなし |
| Ben — 高額のローン、長い借入期間 | 中リスク → Action Center に人的タスクが発生 |
| Clara — 若年、収入が厳しい | 高リスク → Action Center に人的タスクが発生 |

Ben と Clara については、プロセスが一時停止している間に **Action Center** を開いてください。クレジットスコアとリスクバンドがあらかじめ入力された状態で、ローン担当者用ダッシュボードが表示されるはずです。判断を送信し、フローが対応する終了状態へ進むことを確認しましょう。

!!! tip "実行トレースを確認する"
    Orchestrator では、実行中のフローインスタンスをクリックすると、アクティブなノードがハイライトされたライブの図を確認できます。各条件分岐が正しく振り分けられているかを確かめるには、これが最速の方法です。
