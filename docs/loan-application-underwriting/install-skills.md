# UiPath スキルのインストール
コーディングエージェント、UiPath CLI、そしてエージェントが Studio ワークフロー・コーデッドエージェント・React アプリ・Maestro プロセスを生成するために必要な知識を与えるスキルをインストールします。

## 1. UiPath CLI をインストールする

```bash
npm install -g @uipath/cli@latest
```

確認: `uip --version` — `1.195.1` 以降が表示されるはずです。

## 2. UiPath スキルをコーディングエージェントにインストールする

=== "Claude Code"

    ```bash
    # 1. マーケットプレイスを追加する（初回のみ）
    claude plugin marketplace add https://github.com/UiPath/skills
    # 2. そこからプラグインをインストールする
    claude plugin install uipath@uipath-marketplace
    uip skills install
    ```

=== "Codex"

    ```bash
    # 1. マーケットプレイスを追加する（初回のみ）
    codex plugin marketplace add UiPath/skills --ref main
    uip skills install
    ```

次のような出力が表示されるはずです。

```json
{
  "Result": "Success",
  "Code": "SkillsInstall",
  "Data": {
    "RootDir": "/Users/YourUser",
    "Skills": [
      "uipath-admin",
      "uipath-agents",
      "uipath-api-workflow",
      "uipath-automation-discovery",
      "uipath-coded-apps",
      "uipath-data-fabric",
      "uipath-feedback",
      "uipath-governance",
      "uipath-human-in-the-loop",
      "uipath-maestro-bpmn",
      "uipath-maestro-case",
      "uipath-maestro-flow",
      "uipath-mcp-servers",
      "uipath-planner",
      "uipath-platform",
      "uipath-review",
      "uipath-rpa",
      "uipath-solution",
      "uipath-tasks",
      "uipath-test",
      "uipath-troubleshoot"
    ],
    "Agents": [
      "claude",
      "codex"
    ],
    "Installed": 42
  }
}
```

出力に次のスキルが含まれていることを確認してください。

- `uipath-rpa` — Studio の XAML 受付ワークフロー用
- `uipath-agents` — Python / LangGraph の与信審査エージェント用
- `uipath-coded-apps` — React 製のローン担当者用ダッシュボード用
- `uipath-maestro-flow` — Maestro のオーケストレーションプロセス用

各スキルは、UiPath プラットフォームのそれぞれの領域に関する深い知識をエージェントに与えます。

| スキル | 何を知っているか |
|---|---|
| **uipath-rpa** | Studio の XAML 構造、アクティビティライブラリ、セレクター、エラーハンドリング、Orchestrator のアセット、パッケージング |
| **uipath-agents** | Python エージェントのプロジェクト構成、LangGraph のパターン、ツール定義、UiPath AI Trust Layer |
| **uipath-coded-apps** | React / TypeScript のアプリ構造、`@uipath/uipath-typescript` SDK、`action-schema.json`、公開手順 |
| **uipath-maestro-flow** | Flow JSON の構造、ノードの種類、条件式、変数のマッピング、プロセスの公開 |

## 3. Coded Apps 用ツールをインストールする

Coded Apps のスキルには、追加の CLI ツールが必要です。

```bash
uip tools install @uipath/codedapp-tool
```

コーデッドアプリ用ツールが利用可能になっていることを確認します。

```bash
uip tools list
```

## 4. テナントに対して認証する

```bash
uip login --authority https://cloud.uipath.com --organization tpenlabs -t CodingAgentsPractice
```

## 5. プロジェクトを開いてセッションを開始する

```bash
cd my-project && claude
# または
cd my-project && codex
```

スキルはセッション開始時に自動的に検出されます。コーデッドエージェントを作るよう依頼すれば、適切なスキルが自動的に読み込まれます。
