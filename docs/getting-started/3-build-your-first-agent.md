# 初めてのエージェントを作る

!!! tip "このレッスンの進め方"

    1. サンプルファイルを入れた作業フォルダーを用意します。
    2. UiPath のエージェントスキルを使って、**Claude Code** にシンプルなエージェントを生成してもらいます。
    3. ソリューションのスキャフォールド、スキーマの設定、検証までの流れを観察します。
    4. **Studio Web** に公開して実行し、結果を確認します。

## ゴール

このレッスンの目的は、気の利いた何かを作ることではありません。これ以降すべてのエージェントで使うことになる **「構築して公開する」ワークフロー** を身につけることです。Claude Code で小さなローコードエージェントを生成し、ソリューションがどのようにスキャフォールドされるのかを見て、実行できる状態まで持っていきます。エージェント自体はあえてシンプルにしてあります。焦点を当てたいのは「説明する → 生成する → 検証する → 公開する → 実行する」というループそのものだからです。

## 何を作るのか

**保険金請求の受理可否（Claims Eligibility）チェック** です。請求（FNOL）の PDF と、そこで参照されている保険証券が与えられると、エージェントは 5 つの簡易なしきい値チェックを順番に実行し、最初のハードな不合格が出た時点で停止します。

1. **保険証券のステータス** — 証券は Current / Paid か（Lapsed / Cancelled / Expired ではないか）？
2. **本人確認** — 請求者は証券の記名被保険者と一致するか？
3. **住所** — 請求書と証券の住所は一致するか？
4. **補償期間** — 事故は証券の有効期間内に発生したか？
5. **請求期限** — 損害発生から 60 日以内に請求されているか？

このエージェントは PDF をそのまま直接読み取ります。追加のセットアップは不要です。（以降の演習では、コンテキストやツール、構造化された抽出処理を備えた、より本格的なエージェントを構築します。）判定ロジックと出力の構造は下記のとおりで、いずれも Claude Code に貼り付けて使います。

## 手順

### 1. 作業フォルダーを用意する

空のフォルダーを作成し、そこにサンプルの請求書 PDF と保険証券 PDF を追加します（PDF は後述のサンプルからダウンロードしてください）。

```bash
mkdir first-agent
cd first-agent
mkdir samples
```

<details markdown="1">
<summary>任意の手順: 自分の規約を定義する（AGENTS.md）</summary>

本格的に作り始める前に、命名規則・構造・「*ワークフローは小さく保つ。すべてを 1 つのフォルダーに詰め込まない*」といったルールを書いた小さなファイルをフォルダーに置いておきましょう。

- コーディングエージェントはこのファイルを自動的に読み、新しいセッションのたびに従ってくれます。
- プロンプトだけがすべてではありません。この Markdown ファイルはエージェントの方向づけに役立ち、セッションをまたいでも、エージェントを変えても、出力の一貫性を保てます。
- 現時点でファイル名は統一されていません（**`CLAUDE.md`** / **`AGENTS.md`** / **`GEMINI.md`** など）。複数のエージェントを使う予定なら、実体のファイルを 1 つだけ置き、名前が異なるエージェント向けにはシンボリックリンクを張るのがベストプラクティスです。
- 以下は出発点となるサンプルです。必要に応じて拡張してください。

```markdown
# 新しいプロジェクトを作るとき

- このワークスペースフォルダーで何かを作るよう依頼されたら、ワークスペース直下で作業せず、新しいプロジェクトフォルダー（短く、小文字、ハイフン区切り）を作成すること。
- 既存のリポジトリの内側でない限り、`git init` で初期化すること。
- 本格的な実装に入る前に、プロジェクト単位の `AGENTS.md`（このファイルのようなもの）を追加し、以降のセッションでも同じ振る舞いが保たれるようにすること。
- 実装・検証・ファイル編集はすべて、その新しいプロジェクトフォルダーの中で続けること。

# UiPath プロジェクト

- 依頼に UiPath、RPA、Orchestrator、Maestro、Studio Web、`.xaml`、`.flow`、`.bpmn`、コンテキストグラウンディング、キュー、アセット、ロボット、ジョブ、トリガー、`uip` が含まれる場合は、インストール済みの UiPath エージェントスキルを適宜使用すること。
- セットアップ、検証、ビルド、パッケージング、実行、プラットフォーム操作には uip CLI を優先して使うこと。
- UiPath Cloud / Orchestrator のリソース（パッケージ、フォルダー、キューアイテムなど）を公開・デプロイ・削除・変更する前には、必ず確認を取ること。
```
</details>

### 2. コーディングエージェントを開いて始める

下記の請求書ファイルと保険証券ファイルのペアを、先ほど作成したフォルダー内の "samples" フォルダーにダウンロードしてください。各請求書は証券番号で対応する証券を参照しており、必ず **対応する** 証券と組み合わせて実行する必要があります。入力ドキュメントにも軽く目を通しておきましょう。

| 請求書（Claim） | 保険証券（Policy） | シナリオ |
| :--- | :--- | :--- |
| [CLM-2026-357861-claim.pdf](assets/claim-samples/CLM-2026-357861-claim.pdf) | [HO-5534416561.pdf](assets/claim-samples/HO-5534416561.pdf) | ムンバイ（INR）— 水濡れ損害、Rajesh Kumar Sharma |
| [CLM-2026-896147-claim.pdf](assets/claim-samples/CLM-2026-896147-claim.pdf) | [HO-3883873532.pdf](assets/claim-samples/HO-3883873532.pdf) | メルボルン（AUD）— 火災損害、Mei Lin Tan |

そのフォルダーでコーディングエージェントを開き、以下の指示を与えてください。

```text hl_lines="3-5 24-64"
UiPath のエージェントスキルを使って、"claims-eligibility-agent" という名前のローコードエージェントを生成してください。このエージェントは、請求書（claim）と保険証券（policy）の 2 つの PDF ファイルを入力として受け取ります。両方の PDF を読み取り、保険証券に照らして請求内容を検証します。

入力:
- in_ClaimPDF — 請求者が提出した事故受付通知（FNOL: First Notice of Loss）の請求フォーム（PDF）。
- in_PolicyPDF — その請求が参照している住宅総合保険の保険証券（PDF）。

エージェントが 2 つの入力ドキュメント間で確認すべき項目:
1. 保険証券ステータスの確認（Policy Status Check）。保険証券上の Payment Status を探します。許容されるステータスは
   "Current" と "Paid" です。"Lapsed"、"Cancelled"、"Expired" の場合はこのチェックは不合格とします。
2. 本人確認（Identity Verification）。請求書上の Claimant Name と、保険証券上の Named Insured を比較します。
   軽微な差異（愛称、ミドルネーム、軽微なスペルの揺れ）は許容します。明らかに別人を指している場合は
   このチェックは不合格とします。
3. 物件住所の一致確認（Property Address Match）。請求書と保険証券に記載された物件住所を比較します。
   表記の揺れ（例: "St." と "Street"）は正規化して比較します。異なる場合はこのチェックは不合格とします。
   本演習には独立した事故報告書が存在しないため、report_address には
   "N/A — no incident report in this exercise" を設定してください。
4. 補償期間の確認（Coverage Period Check）。Incident Date が保険証券の Effective Date 以降、かつ
   Expiration Date 以前であることを確認します。この期間外であればこのチェックは不合格とします。
5. 請求期限の確認（Filing Deadline Check）。Incident Date と Date of Submission の間の暦日数を計算します。
   60 日を超えている場合は、請求書に遅延理由の説明があるかどうかを確認します。説明がなければ不合格とします。

エージェントは必ず以下の構造に一致する出力を返す必要があります。この出力は後続のアプリやエージェントで利用されます:

{
  "out_isEligible": "boolean — 請求が審査の対象として受理できるかどうか",
  "out_EligibilityAnalysisSummary": "string — 判定理由の簡潔でわかりやすい説明",
  "out_EligibilityChecksJSON": {
    "claim_id": "string",
    "policy_number": "string",
    "escalate": "boolean — この請求に人によるさらなる確認が必要かどうか",
    "checks": {
      "policy_status": {
        "result": "pass | fail",
        "detail": "string"
      },
      "identity_match": {
        "result": "pass | fail",
        "claimant_name": "string",
        "policyholder_name": "string",
        "detail": "string"
      },
      "address_match": {
        "result": "pass | fail",
        "claim_address": "string",
        "policy_address": "string",
        "detail": "string"
      },
      "coverage_period": {
        "result": "pass | fail",
        "incident_date": "string",
        "effective_date": "string",
        "expiration_date": "string",
        "detail": "string"
      },
      "filing_deadline": {
        "result": "pass | fail ",
        "incident_date": "string",
        "claim_date": "string",
        "days_elapsed": "number",
        "detail": "string"
      }
    }
  }
}


- すべてのチェックが合格 → out_isEligible = true、それ以外は false
- 問題が「遅延提出だが正当な理由がある」場合のみ → out_isEligible = true、"escalate" = true
- ドキュメントに明示されていない情報をエージェントが推測してはならない旨を、プロンプト内で明確に記載してください。
- これは物件損害に関する FNOL / 保険金請求の受理可否プロセスです。この業務で一般的に考慮される観点と業界のベストプラクティスを踏まえたプロンプトを書いてください。

エージェントが処理するサンプルドキュメントが samples サブフォルダーにいくつか置かれています。
```

### 3. スキャフォールドの様子を見る

Claude Code は、おおむね次の順序で作業を進めます（各ステップを都度承認してください）。

- **ソリューション** を作成し、その中にエージェントを初期化する
- エージェントプロジェクトをソリューションに追加する
- **システムプロンプト** を記述し、**入出力スキーマ** を設定する（ファイル入力 2 つ、出力 3 つ）
- **validate** を実行して、その構成が Studio Web でサポートされていることを確認する

<details markdown="1">
<summary>実際の出力例</summary>
- これは UiPath のローコードエージェントを作成するタスクなので、uipath-agents スキルを使います。エージェントのファイルを作る前に、**スキルの手順** と既存プロジェクトの構成を確認します。
- 依頼には明示的に「ローコード」とあるため、agent.json ベースの **Agent Builder プロジェクト** として扱います。既存の構造を壊さないよう、すでにエージェントやソリューションのスキャフォールドがあるかを確認しています。
- ワークスペースには既存のプロジェクトスキャフォールドはなく、サンプル PDF だけがあります。生成するファイルが UiPath の想定するスキーマとライフサイクルに沿うよう、次にローコードエージェントのガイダンスを読みます。
- ローコードのワークフローでは、スキャフォールドの前にローカルの uip solution コマンドを確認する必要があります。新しいバージョンの CLI で solution new が solution init に改称されたためです。いまその確認を行い、サポートされているコマンドでプロジェクトを作成します。
- 実行したコマンド: `$ uip solution init --output json`
- この CLI は `uip solution init` に対応しているため、現行のライフサイクルを使います。スキャフォールドしたエージェントを書く前に、ローコードの JSON、プロンプト、ファイル添付、検証に関するリファレンスを読みます。
- ここで重要な制約は、添付ファイル入力はプロンプト上ではメタデータしか参照できないという点です。UiPath 組み込みの Analyze Files ツールを追加し、受理可否を判断する前に両方の PDF に対して必ずこのツールを呼び出すよう、エージェントに明示的に指示します。
- これは入力から出力を導く受理可否の判断なので、autonomous エージェントのバリアントを使います。スキャフォールドしてファイルを修正する前に、autonomous 固有のルールを確認します。
- スキャフォールドのデフォルトモデルをそのまま使うべきではないので、テナントのモデル一覧を確認します。
- エージェントのプロンプトが探すべきフィールド名を正しく指定し、想定される文書の言い回しに対応できるよう、いまサンプルの請求書・保険証券のテキストを読んでいます。
- サンプルを見ると、必要なフィールドはすべて明示されています: 請求番号、提出日、請求者、証券番号、物件住所、事故日、保険料の支払いステータス、記名被保険者、保険期間、対象物件です。これから、ソリューションと、claims-eligibility という名前のスタンドアロンな autonomous ローコードエージェントをスキャフォールドします。
- ソリューションのスキャフォールドを作成できました。プロジェクトがソリューションのマニフェストに登録されるよう、その中にローコードエージェントのプロジェクトを追加します。
- 実行したコマンド: `$ uip agent init claims-eligibility-solution/claims-eligibility --output json`
- エージェントのスキャフォールドが正しく登録されました。生成された JSON ファイルを修正する前に内容を読み、サポートされているソースファイルだけを変更して、派生ファイルは refresh に再生成させるようにします。
- ソース側に 2 か所の変更を加えます。スキャフォールドのプロンプトとスキーマを受理可否チェックの仕様に置き換えることと、Analyze Files 組み込みツールのリソースを追加することです。そのあとで uip agent refresh と uip agent validate を実行し、派生ファイルを手書きせず CLI に再生成させます。
- いまプロンプト、添付ファイルのスキーマ、型付きの出力仕様、組み込みツールの定義を適用しています。プロンプトでは、ドキュメントの記載を超えた推測を明確に禁止し、最終的な補償の可否判断ではなく受理可否のスクリーニングに範囲を限定しています。
- ソースファイルの修正が完了しました。まず JSON のパースチェックを行い、そのあとで UiPath の refresh / validation を実行して、entry-points.json と bindings_v2.json を手書きではなく生成させます。
- JSON のパースが通りました。次に uip agent refresh を実行します。
- スキーマは完全に一致しています。もう一度 CLI のマイグレーションを実行します。
- マイグレーションが完了し、ビルダー用の成果物が生成されました。最終的なプロジェクト状態を確認するため、読み取り専用の検証を実行します。
- 実行したコマンド: `$ uip agent validate claims-eligibility-solution/claims-eligibility --output json`
- 検証に成功しました。作成したものと、PDF 添付を使ったテストに関する注意点を正確に報告できるよう、最後にファイルとステータスを確認します。
- プロジェクトはローカルで有効であり、生成された .agent-builder ファイルも存在します。ビルド出力に Analyze Files リソースが確実に含まれるよう、生成されたバインディングを一度確認します。

- UiPath のローコード autonomous エージェント claims-eligibility を実装しました。

作成したソリューションとエージェントのファイル:

- claims-eligibility-solution/claims-eligibility/**agent.json**
- claims-eligibility-solution/claims-eligibility/**resources/AnalyzeFiles/resource.json**
- claims-eligibility-solution/claims-eligibility/**entry-points.json**

設定内容:

- 入力: in_ClaimPDF、in_PolicyPDF をジョブ添付の PDF 入力として設定
- toolType: "analyze-attachments" を使用した組み込みの Analyze Files ツール
- 依頼どおりの出力スキーマ
- out_isEligible、out_EligibilityAnalysisSummary、ネストされた out_EligibilityChecksJSON
- 保険証券ステータス、本人確認、住所、補償期間、請求期限、根拠のない推測の禁止、物件保険金請求の受理可否に関するベストプラクティスを網羅したシステムプロンプト

</details>

### 4. アップロードして Studio Web で開く

エージェントのビルドとローカル検証が完了しました。続けて次のように尋ねます。

```text
いいですね！ このエージェントを Studio Web で実行するには、次に何をすればよいですか？
```

エージェントは次のように提案してくれます。

```text
以下のコマンドでソリューションをアップロードしてください:

   $ uip solution upload claims-eligibility-solution --output json

これで DesignerUrl が返ってくるはずです。

その URL を Studio Web で開き、claims-eligibility エージェントを開いて、run / test の画面で次の値を指定してください:
   in_ClaimPDF: samples/ にある請求書 PDF のいずれか
   in_PolicyPDF: それに対応する保険証券 PDF
```

コマンドを実行し、返ってきた DesignerURL を開いてみましょう。

![エージェントをスキャフォールドする Claude Code: ソリューションを作成し、エージェントを初期化し、スキーマを設定したところ](3-build-your-first-agent.images/fresh-from-oven.png){ .screenshot }


請求書とその保険証券の組み合わせで実行し、構造化された判定結果を読み取ってみてください。ここまでで、構築・公開・実行という一連のサイクルを 1 周したことになります。以降の演習で扱う、より本格的なエージェントに進む準備が整いました。

### 5. サンプルの請求書を実行する

Studio Web で **Debug** をクリックし、2 つのファイル入力を指定してエージェントを実行します。

1. **in_ClaimPDF** に `CLM-2026-896147-claim.pdf` を指定します。
2. **in_PolicyPDF** に `HO-3883873532.pdf` を指定します。
3. **Run**（または **Save & Debug**）を選択します。

実行が完了したら出力を開きます。スキーマで定義した 3 つのフィールド（`out_isEligible`、`out_EligibilityChecksJSON`、`out_EligibilityAnalysisSummary`）が確認できます。

請求 `CLM-2026-896147` の場合、エージェントは **受理不可（ineligible — deny）** と判断するはずです。この請求は 60 日の期限を大きく過ぎてから提出されているためです。

```json
{
  "out_isEligible": false,
  "out_EligibilityAnalysisSummary": "請求 CLM-2026-896147 は審査の対象として受理できません。5 つの受理可否チェックのうち 4 つは合格しています。保険証券は有効かつ保険料が全額支払済みであり、請求者名は記名被保険者と一致し、物件住所も一致しています。また事故日 14/04/2026 は保険証券の満了日にあたりますが、満了日当日は補償期間に含むものとして扱っています。一方で請求期限のチェックは不合格です。この請求は事故日から 83 暦日が経過してから提出されており、保険証券に定められた 60 日以内という提出要件を超えています。さらに、請求フォームのどこにも遅延の理由が記載されていません。遅延提出に正当な理由が示されていないため、この請求は受理できません。",
  "out_EligibilityChecksJSON": {
    "claim_id": "CLM-2026-896147",
    "policy_number": "HO-3883873532",
    "escalate": false,
    "checks": {
      "policy_status": {
        "result": "pass",
        "detail": "保険証券の支払いステータスは 'Current - Paid in Full' と明記されています。"
      },
      "identity_match": {
        "result": "pass",
        "claimant_name": "Mei Lin Tan",
        "policyholder_name": "Mei Lin Tan",
        "detail": "請求者名 'Mei Lin Tan' は記名被保険者 'Mei Lin Tan' と完全に一致しています。"
      },
      "address_match": {
        "result": "pass",
        "claim_address": "4/16 Chapel Street, St Kilda, VIC 3182",
        "policy_address": "4/16 Chapel Street, St Kilda, VIC 3182",
        "detail": "請求書の物件住所 '4/16 Chapel Street, St Kilda, VIC 3182' は、保険証券に記載された対象物件の住所と完全に一致しています。report_address=N/A - no incident report in this exercise。"
      },
      "coverage_period": {
        "result": "pass",
        "incident_date": "14/04/2026",
        "effective_date": "14/04/2025",
        "expiration_date": "14/04/2026",
        "detail": "事故日 14/04/2026 は保険証券の満了日にあたり、満了日当日は補償期間に含むものとして扱います。事故日は 14/04/2025 から 14/04/2026 までの補償期間内です。"
      },
      "filing_deadline": {
        "result": "fail",
        "incident_date": "14/04/2026",
        "claim_date": "06/07/2026",
        "days_elapsed": 83,
        "detail": "事故日（14/04/2026）から提出日（06/07/2026）までに 83 暦日が経過しており、保険証券の Section III, Condition 1 に定められた 60 日の請求期限を超えています。請求フォームには遅延の理由が記載されていません。正当な理由のない遅延提出のため、この請求は受理できません。"
      }
    }
  }
}
```

!!! note "文言は毎回変わります"
    LLM を使っているため、`detail` や要約のテキストは生成されるものであり、一字一句同じにはなりません。一致しているべきなのは構造と、各チェックの `result` です。

ほかの請求サンプルでも試してみてください。

これで完了です。Claude Code でエージェントを構築し、公開し、実行しました。最初の 1 周が終わり、これ以降のすべての土台ができました。
