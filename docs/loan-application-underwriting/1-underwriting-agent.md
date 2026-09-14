# AI による与信審査
`uipath-agents` スキルを使って、UiBank API からローンのデータを取得し、財務指標を計算し、LLM にその結果を解釈させて与信審査の結果を生成する Python / LangGraph エージェントを生成します。

## 1. プロジェクトフォルダーをコーディングエージェントで開く

`LoanUnderwritingAgent` という名前の空のフォルダーを作成し、コーディングエージェント（Claude Code、Codex など）で開きます。

```bash
mkdir LoanUnderwritingAgent
```

## 2. エージェントの内容を説明する

作りたいものを、コーディングエージェントに平易な言葉で説明します。

```text
次の処理を行う UiPath のコーデッドエージェントを LangGraph で構築してください:

1. loan_id を入力として受け取る
2. UiBank API（https://uibank-api.uipath.com/explorer/swagger.json、認証不要）を呼び出してローン見積を検証し、
   申込者の借入希望額（loan amount）、借入期間（loan term）、年収（yearly income）、年齢（age）を抽出する
3. 市場水準との比較のため、UiBank の全申込における平均借入額を取得する
4. 加工前の財務指標を計算して LLM に提示する: 月々の返済額、債務所得比率（月々の返済額が月収に占める割合）、
   および当該ローンが市場平均と比べてどの水準にあるか
5. LLM にそれらの指標を解釈させ、クレジットスコア（0〜100）とリスクバンド（Low / Medium / High）を付与し、
   平易な言葉での審査サマリーを生成する

5 件のケースからなる eval セットも含めてください。エージェントの名前は {YourName}LoanUnderwritingAgent とします。UiPath SDK を使用してください。
```

コーディングエージェントは `uipath-agents` スキルのコンテキストを読み取り、完全なエージェントプロジェクトを生成します。

- `main.py` — LangGraph のグラフ定義を含むエージェントのエントリーポイント（ツールはここに書かれる場合も、別の `tools.py` に分かれる場合もあります）
- `pyproject.toml` — `uipath-langgraph` を依存関係に含むプロジェクト設定
- `evals/` — 5 件の評価ケースが入ったフォルダー

## 3. 生成されたコードをレビューする

プロジェクトを IDE で開きます。コーディングエージェントごとに生成されるコードは少しずつ異なり、構成にも幅があります。重要なのは、必要な要素が揃っているかどうかです。

**確認すべきポイント:**

- **`@tool` デコレーターの付いた 3 つの関数** — `verify_quote`、`get_average_loan_amount`、`compute_financial_metrics` に対応するものです。別ファイルの `tools.py` にあっても、すべて `main.py` の中にあっても構いません。
- **システムプロンプト** — 財務指標を総合的に解釈し、クレジットスコア・リスクバンド・審査サマリーを生成するよう LLM に指示する `SYSTEM_PROMPT` 文字列です。通常は別ファイルではなく `main.py` にインラインで、プレーンなプロンプト文字列として組み立てられます。
- **エージェントのエントリーポイント** — `langgraph.json` で定義され、`main.py:graph`（`graph = builder.compile()` の部分）を指します。これは `entry-points.json` にも `"agent"` エントリーポイントとして登録されます。
- **`evals/`** — さまざまなリスクプロファイルを網羅した 5 件のテストケース。`uipath eval` でエージェントのスコアリング挙動を検証するために使います。

システムプロンプトを確認してください。しきい値を固定のスコアに機械的に対応づけるのではなく、指標の組み合わせについて推論し、自然言語で説明を生成するよう LLM に指示しているはずです。プロンプトが機械的すぎる場合は、コーディングエージェントに次のように依頼します。

```text
システムプロンプトを修正して、固定のルールを当てはめるのではなく、複数の要因の組み合わせについて
LLM が推論するようにしてください。たとえば、DTI が高くても借入額が小さい場合と、同じ DTI で
借入額が大きい場合とでは、扱いが変わるべきです。
```

## 4. エージェントをローカルでテストする

### 1. プロジェクトフォルダーに移動する

ターミナルを開き、作成した `LoanUnderwritingAgent` フォルダーに移動します。

```bash
cd "/path/to/your/LoanUnderwritingAgent"
```

パスは、お使いのマシン上の実際の場所に置き換えてください。

### 2. エージェントを実行して確認する

次のプロンプトをコーディングエージェントに渡してください。さまざまなリスクプロファイルにまたがる実在のローン ID を探し、それぞれでエージェントを実行し、出力を確認してくれます。

```text
いま構築した LoanUnderwritingAgent をテストしてください。

1. UiBank の Swagger ドキュメントを開いて内容を確認してください:
   https://uibank-api.uipath.com/explorer/swagger.json

2. ドキュメントに記載された読み取り専用のエンドポイントのみを使い、リスクプロファイルに幅がある
   既存のローン見積を 3 件見つけてください。たとえば、収入とのバランスが良好な少額のローン、
   期間の長い高額のローン、収入に対する借入額の比率が厳しい申込者、といった具合です。

   要件:
   - データの作成・更新・削除は一切行わないこと。
   - loan_id を捏造したり、存在を確認していない ID を使い回したりしないこと。各レコードが実在することを検証すること。

3. 各 loan_id について、コーデッドエージェントを実行し、結果をそれぞれ別の出力ファイルに保存してください。

4. 各 out-*.json を読み、次の内容が含まれていることを確認してください:
   - 0 から 100 の間の credit_score
   - Low、Medium、High のいずれかの risk_band
   - 一般論ではなく、実際に指標（債務所得比率、市場平均との比較）に基づいて推論した、
     平易な言葉での審査サマリー

5. 次の表形式で報告してください: loan_id | 借入額 | 期間 | 収入 | 年齢 | クレジットスコア | リスクバンド。
   不審な点（プロファイルが大きく異なるのにスコアが同一、フィールドの欠落、例外の発生など）があれば
   指摘してください。
```

## 5. エージェントをデプロイする

まず仮想環境を有効化します。

=== "Mac / Linux"
    ```bash
    source .venv/bin/activate
    ```

=== "Windows"
    **コマンドプロンプト:**
    ```bash
    .venv\Scripts\activate
    ```
    **PowerShell**（必要に応じて、先にスクリプトの実行を許可します）:
    ```bash
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    .\.venv\Scripts\Activate.ps1
    ```

### エージェントを公開する

セットアップと初期化を実行します。

```bash
uip codedagent setup --force
```

```json
{
 "Result": "Success",
 "Code": "CodedAgentsSetup",
 "Data": {
  "PythonPath": "python3.14",
  "Package": "uipath",
  "PackageInstalled": "Yes",
  "PackageVersion": "2.10.73"
 }
}
```

テナントを設定し、ログイン状態を確認します。

```bash
uip login tenant set CodingAgentsPractice --output json
```

```json
{
  "Result": "Success",
  "Code": "TenantSet",
  "Data": {
    "Name": "CodingAgentsPractice",
    "Id": "30231678-ca53-438f-8258-4ef8c6cfa266"
  }
}
```

```bash
uip login status --output json
```

```json
{
  "Result": "Success",
  "Code": "LogIn",
  "Data": {
    "Status": "Logged in",
    "Organization": "tpenlabs",
    "Tenant": "CodingAgentsPractice",
    "Expiration Date": "2026-06-29T14:08:47.000Z"
  }
}
```

UiPath プロジェクトを初期化します。これによりエントリーポイント、Mermaid 図、プロジェクトマニフェストが生成されます。

```bash
uip codedagent init
```

```text
'bindings.json' already exists, skipping.
✓  Created 'entry-points.json' file with 1 entrypoint(s).
✓  Created 1 mermaid diagram file(s).
✓  Updated 'project.uiproj' file.
✓  Updated: CLAUDE.md, CLI_REFERENCE.md, SDK_REFERENCE.md, AGENTS.md, REQUIRED_STRUCTURE.md

  Entrypoint: agent
  ──────────────────────────────────────────────────

      ┌───────────┐
      │ __start__ │
      └─────┬─────┘
         │
         ▼
    ┌ node ─────────────┐
    │ verify_loan_quote │
    └─────────┬─────────┘
         │
         ▼
   ┌ node ────────────────┐
   │ get_market_benchmark │
   └───────────┬──────────┘
         │
         ▼
     ┌ node ───────────┐
     │ compute_metrics │
     └────────┬────────┘
         │
         ▼
     ┌ node ─────────┐
     │ assess_credit │
     └───────┬───────┘
         │
         ▼
       ┌─────────┐
       │ __end__ │
       └─────────┘
```

### エージェントをデプロイする

```bash
uip codedagent deploy --tenant
```

```text
⠋ Packaging project ...
Name       : {YourName}LoanUnderwritingAgent
Version    : 0.0.1
Description: Loan underwriting agent that assesses UiBank loan quotes with LLM-driven credit scoring
Authors    : {YourName}
✓  Project successfully packaged.
⠋ Publishing most recent package: {YourName}LoanUnderwritingAgent.0.0.1.nupkg ...
✓  Package published successfully!
```

### プロセスを作成する

まず、パッケージとそのエントリーポイントを確認します。

```bash
uip or packages list --search "{YourName}LoanUnderwritingAgent" --output json
```

```bash
uip or packages entry-points "{YourName}LoanUnderwritingAgent:0.0.1" --output json
```

続いてプロセスを作成します。

=== "Mac / Linux"
    ```bash
    uip or processes create \
      --name "{YourName}LoanUnderwritingAgent" \
      --package-key "{YourName}LoanUnderwritingAgent" \
      --package-version "0.0.1" \
      --entry-point "agent" \
      --folder-key "c30345cd-5543-46a9-b42b-0354e60b4f15" \
      --output json
    ```

=== "Windows (PowerShell)"
    ```bash
    uip or processes create `
      --name "{YourName}LoanUnderwritingAgent" `
      --package-key "{YourName}LoanUnderwritingAgent" `
      --package-version "0.0.1" `
      --entry-point "agent" `
      --folder-key "c30345cd-5543-46a9-b42b-0354e60b4f15" `
      --output json
    ```

### テスト用のローン ID を探す

UiBank から有効なローン ID を見つけるよう、コーディングエージェントに依頼します。

```text
UiBank の Swagger ドキュメントを開いて内容を確認してください:

https://uibank-api.uipath.com/explorer/swagger.json

API に記載されているエンドポイントのみを使い、ローン見積を取得するための読み取り専用エンドポイントを
特定してください。GET リクエストを実行し、現在 UiBank に存在する loan_id を 1 件返してください。

要件:
- データの作成・更新・削除は一切行わないこと。
- ID を捏造したり、存在を確認していない ID を使い回したりしないこと。
- 返すレコードが実在することを検証すること。
- loan_id と、エージェントを実行するための PowerShell コマンドを返すこと。
- JSON は PowerShell 向けに正しくエスケープすること。
```

### デプロイ済みエージェントを Orchestrator から実行する

**Orchestrator** で **CodingAgentsILT** フォルダーを開き、`{YourName}LoanUnderwritingAgent` を選択して、コーディングエージェントが返した `loan_id` を入力引数に指定して実行を開始します。ジョブの出力で、クレジットスコア、リスクバンド、審査サマリーを確認してください。
