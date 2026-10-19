# 3. Maestro Flow によるオーケストレーション

`uipath-maestro-flow` スキルを使って、コーデッドエージェントとローン担当者用ダッシュボードをつなぎ、リスクバンドに応じて申込を振り分ける UiPath Flow プロセスを生成します。

!!! info "このレッスンで作るもの"
    ```
    開始 → エージェント呼び出し → risk_band == "Low" ?
                                    ├─ Yes → 自動承認して終了
                                    └─ No  → 人的レビュー（アプリを表示）
                                              → officer_decision == "Approve" ?
                                                  ├─ Yes → 承認して終了
                                                  └─ No  → 却下して終了
    ```
    どの経路を通っても `final_decision`（`Approved` / `Rejected`）を返します。

!!! warning "前提の確認"
    このレッスンは、レッスン1 と レッスン2 の成果物を参照します。先に次を確認してください。

    - レッスン1 のエージェントが **6 項目**を返すこと
    - レッスン2 のアプリが **{{ practice_folder }}** フォルダーにデプロイ済みであること

!!! tip "始める前に `uip login` を実行し直してください"
    **`uip` のセッションは約 1 時間で切れます。** このレッスンの所要時間はそれを超えるため、
    途中で認証エラーになることがあります。始める前に入り直しておくと確実です。

    ```bash
    uip login status --output json
    ```

    `ExpirationDate` は **UTC 表記**です。日本時間に直すには 9 時間を足してください。

## 1. ソリューションの中で作業を始める

[レッスン0](0-environment-setup.md) で作ったソリューションに移動します。

```bash
cd LoanApplicationUnderwriting
```

ここをコーディングエージェント（Claude Code、Codex など）で開きます。**フロープロジェクトはコーディングエージェントが
`uip maestro flow init` で作成し、ソリューションへの登録まで自動で行います。**

!!! note "自分でフォルダーを作らないでください"
    Flow プロジェクトは `<ソリューション>/<プロジェクト>/<プロジェクト>.flow` という構成が必要で、
    `uip maestro flow init` がこれを正しく作ります。先に `mkdir` すると、初期化がその場所を避けてしまいます。

## 2. プロセスの内容を説明する

フロー全体を、コーディングエージェントに平易な言葉で説明します。

```text
uipath-maestro-flow スキルを使って、LoanUnderwritingProcess という名前の
UiPath Flow プロセスを構築してください。要件は次のとおりです:

1. 6 つの入力を受け取る: loan_id、applicant_first_name、applicant_last_name、
   loan_amount、loan_term、income
2. エージェント LoanUnderwritingAgent（{{ practice_folder }} フォルダー内）を
   呼び出し、loan_id を渡して、返された値をプロセス変数として保持する:
   credit_score、risk_band、assessment_summary、monthly_repayment、
   debt_to_income_ratio、loan_to_market_ratio
3. risk_band が "Low" の場合は申込を自動承認してプロセスを終了する
4. Medium または High の場合は、アプリ loanofficerdashboard
   （{{ practice_folder }} フォルダー内）を人的タスクとして開き、12 個の入力すべて
   （LoanId、ApplicantFirstName、ApplicantLastName、LoanAmount、LoanTerm、YearlyIncome、
   CreditScore、RiskBand、AssessmentSummary、MonthlyRepayment、
   DebtToIncomeRatio、LoanToMarketRatio）を渡し、officer_decision を受け取る
5. officer_decision に基づいて Approved または Rejected で終了する
6. 自動承認された場合もローン担当者が判断した場合も、いずれのケースでも
   final_decision（string — "Approved" または "Rejected"）を出力する

7. 人的タスクのノードがアプリを正しく解決できるよう、次の 2 点を必ず行ってください:
   - uip solution resources add --source remote --kind App でアプリをソリューションリソースに登録する
   - .flow の bindings[] にアプリ用のバインディング対（name / folderPath）を追加し、
     それをエージェント用のバインディングより前に置く
```

!!! important "要件7 を省略しないでください"
    要件7 は原典にはありませんが、**これを省くと `validate` は通るのに実行時に失敗します。** 理由は[手順3](#3-生成されたフローをレビューする)で説明します。

コーディングエージェントは `uipath-maestro-flow` スキルのコンテキストを読み取り、完全なプロジェクトを生成します。

```
LoanApplicationUnderwriting/                  ← レッスン0 で作ったソリューション
├── LoanApplicationUnderwriting.uipx
├── LoanUnderwritingAgent/                    ← レッスン1 で追加済み
├── resources/solution_folder/
│   └── app/CodedAction/loanofficerdashboard.json
└── LoanUnderwritingProcess/                  ← 今回追加（フロープロジェクト）
    ├── LoanUnderwritingProcess.flow
    ├── operate.json
    └── project.uiproj
```

`uip maestro flow init` の出力に `"SolutionRegistration": { "Status": "Registered" }` とあれば、
ソリューションへの登録まで完了しています。

!!! tip "エージェントはソリューション内の兄弟として参照することもできます"
    レッスン1 のエージェントは同じソリューションの中にあるため、フローから**ローカル参照**できます。

    ```bash
    uip maestro flow registry list --local --output json
    ```

    `(In-solution) LoanUnderwritingAgent` が表示されるはずです。この形で参照すると、**エージェントを先に
    デプロイしなくてもフローを作れます。**

    ただし本コースでは、レッスン1 でデプロイ済みの**公開エージェント**を参照する形で進めます。
    そのほうが各レッスンで動作を確認しながら進められるためです。

## 3. 生成されたフローをレビューする

`LoanUnderwritingProcess.flow` をテキストエディタで開くか、コーディングエージェントに構造を説明させてください。

### ノードとエッジ

- 6 つのプロセス入力変数（`loan_id`、`applicant_first_name`、`applicant_last_name`、`loan_amount`、`loan_term`、`income`）を持つ **Start ノード**
- `loan_id` を入力として `LoanUnderwritingAgent` を呼び出し、**6 つの出力変数**を受け取る **Agent ノード**
- `risk_band == "Low"` で分岐する **Condition ノード**
- `loanofficerdashboard` に接続され、**12 個の変数**がすべて入力としてマッピングされ、`officer_decision` を出力とする **Human Task ノード**
- `officer_decision == "Approve"` で分岐する 2 つ目の **Condition ノード**
- 3 つの **End ノード**（Auto-Approved、Approved、Rejected）

!!! important "エージェントの出力が 6 つあるか"
    Agent ノードの定義（`definitions[]`）にある `outputDefinition.output.schema` を確認してください。**ここに 6 項目すべてが並んでいなければ、フローから参照できません。**

    3 項目しか無い場合は、レッスン1 のエージェントが 3 出力のままです。レッスン1 に戻って修正し、`uip codedagent deploy` → `uip maestro flow registry pull --force` をやり直してください。

### ⚠️ `bindings[]` の順序を必ず確認する

**このレッスンで最も見つけにくい不具合です。** `.flow` の `bindings[]` 配列を開き、**アプリ用のバインディングがエージェント用より前にある**ことを確認してください。

```json
"bindings": [
  {
    "id": "bindingLoanOfficerDashboardName",
    "name": "name",
    "type": "string",
    "resource": "app",
    "resourceKey": "{{ practice_folder }}.loanofficerdashboard",
    "default": "loanofficerdashboard",
    "propertyAttribute": "name",
    "resourceSubType": "CodedAction"
  },
  {
    "id": "bindingLoanOfficerDashboardFolderPath",
    "name": "folderPath",
    "type": "string",
    "resource": "app",
    "resourceKey": "{{ practice_folder }}.loanofficerdashboard",
    "default": "{{ practice_folder }}",
    "propertyAttribute": "folderPath",
    "resourceSubType": "CodedAction"
  },
  {
    "id": "bindingLoanUnderwritingAgentName",
    "...": "エージェント用はこの後ろに"
  }
]
```

!!! danger "アプリ用のバインディングが無いとどうなるか"
    人的タスク（Action App）のノードは、**`bindings[]` 配列で最初に見つかった同名のバインディングを使います。** アプリ用が無いと、エージェント用のものを掴んでしまいます。

    結果、実行時にこうなります。

    ```
    ErrorCode 170015
    No app: LoanUnderwritingAgent found in folder: {{ practice_folder }}
    ```

    **アプリを探しているのにエージェントの名前が出る**のが特徴です。しかも `uip maestro flow validate` は `Valid` を返すため、**実行するまで気づけません。**

アプリがソリューションリソースに登録されていない場合は、手動で追加できます。

```bash
cd LoanUnderwritingProcess
uip solution resources add --source remote --kind App \
  --name "loanofficerdashboard" --folder-path "{{ practice_folder }}" --output json
```

### ⚠️ Studio Web で出る警告について（消そうとしないでください）

生成したフローを Studio Web で開くと、ヘルス アナライザーに次の警告が出ます。

```
結果「Reject」には下流のノードがありません。接続を追加するか、結果を削除してください。
```

**これは表示上のものです。実行時の正しさには影響しません。**

人的タスクには `Approve` / `Reject` の 2 つの outcome を定義していますが、ノードの出力ポートは
`completed` の 1 つだけです。どちらの判断だったかは、そのあとの**判定ノードが
`$vars.officerReview.status` を見て分岐**します。デザイナーは outcome ごとに接続を期待するため、
唯一のエッジを最初の outcome（Approve）に紐づけて表示し、Reject を「未接続」と見なします。

!!! danger "警告を消そうとすると壊れます"
    エッジの出力ポートを `outcome-approve` / `outcome-reject` に分けると、**`uip maestro flow validate` は
    `Valid` を返し、この警告も消えます。** しかし**実行すると誤った経路を通ります。**

    生成される BPMN を見ると、理由は明らかです。

    ```xml
    <bpmn:sequenceFlow sourceRef="officerReview" targetRef="endApproved" />   <!-- 条件なし -->
    <bpmn:sequenceFlow sourceRef="officerReview" targetRef="endRejected" />  <!-- 条件なし -->
    ```

    条件式が付かないため、どちらを通るかが決まりません。実測では **Approve で完了しても
    `final_decision: "Rejected"` が返りました。**

    **判定ノードで分岐する構成のままにしてください。** 承認・却下の両方が正しく動くことを確認済みです。

### 条件の向きを変えたいとき

マッピングや条件の調整が必要な場合は、コーディングエージェントに次のように依頼します。

```text
リスクバンドの条件を修正して、既定の経路が人的レビューのノードに向かい、明示的な条件分岐のほうで
"Low" の自動承認ケースを処理するようにしてください。
```

!!! tip "Studio Web でフローを可視化する"
    ソリューションは **Studio Web** にアップロードでき、Orchestrator にデプロイする前にプロセスの図を確認できます。

    ```bash
    cd LoanApplicationUnderwriting
    uip solution upload . --output json
    ```

    返ってきた `DesignerUrl` をブラウザーで開くと、コーディングエージェントが生成したとおりのノード、条件、接続がキャンバスに描画されます。

!!! warning "確認は内容を確定させてから行ってください"
    **Studio Web で一度開いたソリューションは、CLI から上書きできなくなります。**
    `uip solution upload` が次のエラーを返すようになります。

    ```
    HTTP 500 on POST .../Solution/<id>/Overwrite
    Could not find a part of the path '/storage/azure/.../.project/...'
    ```

    ブラウザーのタブを閉じても解消しません（`uip solution download` での読み出しは可能です）。

    **対処**: `LoanApplicationUnderwriting.uipx` の `SolutionId` を新しい GUID に書き換えて
    `uip solution upload` すると、**新規ソリューションとして作成されます。** 古いほうは次で削除します。

    ```bash
    uip solution delete <古い SolutionId> --yes --output json
    ```

    そのため、**フローが一通りできてから Studio Web で確認する**のがおすすめです。

## 4. テスト用のローン見積を用意する

!!! warning "固定の loan_id は載せていません"
    UiBank は共有のデモ環境で、**データは日々追加され、ときどきリセットされます。** レッスン1 で確定した 3 件がまだ生きていればそれを使ってください。

まず生存を確認します。

```bash
curl -s -o /dev/null -w "%{http_code}\n" {{ uibank_api }}/api/quotes/<loan_id>
```

404 が返る、またはレッスン1 から時間が空いた場合は、次のプロンプトで選び直してください。

```text
UiBank の Swagger ドキュメントを開いて内容を確認してください:
{{ uibank_swagger }}

読み取り専用のエンドポイントのみを使い、リスクプロファイルに幅がある既存のローン見積を 3 件見つけ、
LoanUnderwritingProcess フロー用のテスト入力を生成してください。

要件:
- Swagger 仕様に記載された GET エンドポイントのみを使用すること。
- データの作成・更新・削除は一切行わないこと。
- loan_id を捏造したり、存在を確認していない ID を使い回したりしないこと。
- 選んだローンレコードが実在することを検証すること。
- loan_amount、loan_term、income は同一の検証済みレコードから設定すること。
- loan_term は年数を表し、1、3、5、10 のいずれかでなければならない。
- 申込者名は UiBank が提供しないため、演習用の安全な値を 3 件分つけること。
- 3 件分の JSON オブジェクトを返すこと。

出力形式:
{
  "loan_id": "<VERIFIED_LOAN_ID>",
  "applicant_first_name": "<FIRST_NAME>",
  "applicant_last_name": "<LAST_NAME>",
  "loan_amount": <LOAN_AMOUNT>,
  "loan_term": <1_OR_3_OR_5_OR_10>,
  "income": <YEARLY_INCOME>
}
```

!!! important "リスクバンドは実行して確かめてください"
    `risk_band` は LLM が借入額・期間・債務所得比率・市場平均との比を総合して判断します。**債務所得比率だけで狙ったバンドになるとは限りません。**

    レッスン1 の手順4 で 3 件が Low / Medium / High に分かれることを確認済みであれば、そのまま使えます。確認していない場合は、手順6 の実行結果を見て、分かれていなければ選び直してください。

## 5. 検証して公開する

=== "手動で行う場合"

    生成された `.flow` ファイルがあるフォルダーに移動します。

    ```bash
    cd LoanApplicationUnderwriting/LoanUnderwritingProcess
    ```

    パックする前に、フローを検証します。

    ```bash
    uip maestro flow validate LoanUnderwritingProcess.flow
    ```

    `"Status": "Valid"` が返れば構文上の問題はありません。

    !!! note "`validate` が通っても実行できるとは限りません"
        手順3 で説明した `bindings[]` の問題は、`validate` では検出されません。**必ず手順3 の確認を済ませてください。**

    `command not found` エラーが出る場合は、maestro ツールが未インストールです。

    ```bash
    uip tools install @uipath/maestro-tool
    ```

    !!! note "初回は数分かかることがあります"
        ツールのインストール時に CLI 本体とスキルの更新も走ります。コマンドが返ってこなくても、しばらく待ってください。

    警告があれば修正し、そのうえでパッケージ化と公開を 1 コマンドで行います。

    === "Windows (PowerShell)"
        ```powershell
        cd ..
        uip maestro flow publish "LoanUnderwritingProcess" "$env:TEMP\dist" --version 1.0.0 --output json
        ```

    === "Mac / Linux"
        ```bash
        cd ..
        uip maestro flow publish "LoanUnderwritingProcess" "/tmp/dist" --version 1.0.0 --output json
        ```

    `"Upload"` の `"Status": "OK"` が返れば、パッケージが Orchestrator にアップロードされています。

    続いてプロセスを作成します。

    === "Windows (PowerShell)"
        ```powershell
        uip or processes create `
          --name "LoanUnderwritingProcess" `
          --package-key "LoanUnderwritingProcess.flow.Flow" `
          --package-version "1.0.0" `
          --folder-path "{{ practice_folder }}" `
          --output json
        ```

    === "Mac / Linux"
        ```bash
        uip or processes create \
          --name "LoanUnderwritingProcess" \
          --package-key "LoanUnderwritingProcess.flow.Flow" \
          --package-version "1.0.0" \
          --folder-path "{{ practice_folder }}" \
          --output json
        ```

    返ってきた `Key` がプロセスキーです。手順6 で使います。

=== "コーディングエージェントに任せる場合"

    次のプロンプトをコーディングエージェントに渡してください。検証・公開・デプロイまでを代行してくれます。

    ```text
    いま構築した LoanUnderwritingProcess の Maestro フローを公開してデプロイしてください。

    1. 生成された .flow ファイルを見つけて検証し、報告された警告があれば修正してください。
    2. bindings[] にアプリ用のバインディング対があり、エージェント用より前に置かれていることを
       確認してください。無ければ追加してください。
    3. uip maestro flow publish でバージョン 1.0.0 として公開してください。
    4. Orchestrator の {{ practice_folder }} フォルダーに、公開したパッケージからプロセスを
       作成してください（--folder-path で指定してください）。
    5. プロセスキーを報告してください。
    ```

!!! tip "作り直すときはバージョンを上げてください"
    `.flow` を修正して公開し直す場合、`uip or processes update` では**パッケージのバージョンを切り替えられません。** プロセスを作り直す必要があります。

    ```bash
    uip or processes delete <プロセスキー> --yes --output json
    uip or processes create --name "LoanUnderwritingProcess" \
      --package-key "LoanUnderwritingProcess.flow.Flow" \
      --package-version "1.0.1" --folder-path "{{ practice_folder }}" --output json
    ```

## 6. フロー全体をテストする

Orchestrator からプロセスを 3 回起動します。手順4 で用意した申込ごとに 1 回ずつです。

**Orchestrator** → **{{ practice_folder }}** → `LoanUnderwritingProcess` → 実行

| 申込者 | 想定される経路 |
|---|---|
| 低リスク（少額のローン、十分な収入） | 自動承認、人的タスクなし |
| 中リスク | Action Center に人的タスクが発生 |
| 高リスク | Action Center に人的タスクが発生 |

中・高リスクの申込については、プロセスが一時停止している間に **Action Center** を開いてください。クレジットスコアとリスクバンドがあらかじめ入力された状態で、ローン担当者用ダッシュボードが表示されるはずです。

!!! important "開いたら「Assign to self」をクリックしてください"
    タスクは**未割り当て**の状態で作成されます。開いただけでは **READ ONLY** で、
    Approve / Reject のボタンを押せません。

    画面上部の **「Assign to self」** をクリックすると編集可能になります。

!!! important "12 個すべてに値が入っているか"
    ここが**レッスン1 からの一貫性の最終確認**です。ダッシュボードの 12 項目すべてに値が入っていれば、エージェント → フロー → アプリの経路が正しくつながっています。

    空欄があれば、レッスン1 のエージェント出力か、フローの変数マッピングのどちらかが欠けています。

判断を送信し、フローが対応する終了状態へ進むことを確認しましょう。ジョブの出力に `final_decision` が返っていれば成功です。

!!! tip "実行トレースを確認する"
    Orchestrator では、実行中のフローインスタンスをクリックすると、アクティブなノードがハイライトされたライブの図を確認できます。各条件分岐が正しく振り分けられているかを確かめるには、これが最速の方法です。

### うまくいかないとき

ジョブが失敗しているのに「実行中」に見えることがあります。**Orchestrator のジョブ API は Maestro フローの失敗を隠すことがある**ためです。Maestro 側の API で確認してください。

```bash
uip maestro flow instance list -f <フォルダーキー> --output json
uip maestro flow instance incidents <インスタンスID> -f <フォルダーキー> --output json
```

`ErrorDetails` に `No app: ... found in folder:` と出ていれば、手順3 の `bindings[]` の問題です。

その他の症状は[トラブルシューティング](../troubleshooting.md#maestro-フロー第2部-レッスン3)を参照してください。

---

## このレッスンでできたこと

- エージェントとアプリをつなぐ Maestro フローを構築した
- `risk_band` による分岐（自動承認 / 人的レビュー）が動くことを確認した
- 人的タスクに **12 項目すべてが渡る**ことを確認した
- どの経路でも `final_decision` が返ることを確認した

次は [4. 申込受付とデータ補完](4-intake-enrichment.md) で、このフローを起動する RPA ワークフローを作ります。
