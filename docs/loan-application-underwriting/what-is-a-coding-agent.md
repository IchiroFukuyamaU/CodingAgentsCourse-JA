# コーディングエージェントとは？
コーディングエージェントの仕組みと、UiPath の自動化開発においてなぜ有用なのかを学びます。

コーディングエージェントとは、コードを読み、書き、その意味を推論する AI アシスタントです。単なる入力補完ではありません。次の 1 行を提案するのではなく、平易な言葉で書かれたゴールを理解し、コードベースを調べ、判断を下し、動作するコンポーネントをまるごと生成します。主導権はあなたにあります。生成物をレビューし、修正を指示し、納得できるまで反復します。

現在はいくつものコーディングエージェントが利用でき、それぞれに強みがあります。

- **Claude Code** — Anthropic の CLI ベースのエージェント。ターミナル上で動作し、ファイルシステムと深く統合されています。本演習で使用するのはこれです。
- **Codex CLI** — OpenAI のコマンドライン型コーディングエージェント。同じくターミナル中心のアプローチです。
- **Cursor** — AI を中心に設計された IDE。エディタとの統合が密で、インライン生成や複数ファイルにまたがるコンテキストに強みがあります。
- **Gemini CLI** — Google のターミナル型エージェント。推論能力とロングコンテキストに強みがあります。
- **GitHub Copilot Agent** — VS Code と JetBrains に組み込まれ、エディタ内で完結するワークフローに適しています。

コーディングエージェントが UiPath の開発において特に強力になるのは、スキルのレイヤーがあるからです。UiPath のアクティビティ、API、プロジェクトの作法といったドメイン知識を読み込ませることで、エージェントは汎用的なひな型ではなく、本番で使える自動化コードを生成できるようになります。本演習で使う UiPath スキルは、まさにそのためのものです。

## 全体像（The Mental Model）

どのコーディングエージェントにも、共通して次の 5 つの概念が登場します。

| 概念 | 内容 |
|---|---|
| **Tools（ツール）** | エージェントが実行できる組み込みのアクション。ファイルを読む、bash コマンドを実行する、Web を検索する、コードを編集する、など。 |
| **Skills（スキル）** | 該当するタスクを見つけたときにエージェントが読み込む、ドメイン知識のバンドル。特定の作業に対する「手順書」のようなものです。 |
| **Commands（コマンド）** | 自分で入力する手動のショートカット（`/commit`、`/test`、`/deploy` など）。エージェントではなく、あなたが起動します。 |
| **Hooks（フック）** | ライフサイクルのイベント（編集前、コミット後、セッション開始時など）で自動的に実行されます。ガードレールとして使われます。 |
| **Subagents（サブエージェント）** | メインのエージェントが起動する専門のワーカー。複雑なタスクを並列化したり、切り離して処理したりするために使います。 |

!!! info "プラグイン（Plugins）"
    プラグインは、これらをまとめてパッケージ化したものです。コーディングエージェント向けの Marketplace アプリのようなものと考えてください。本演習で使う UiPath スキルもプラグインです。

## ツールの実際

Claude Code の組み込みツールは常に利用可能で、セットアップは不要です。

| ツール | 機能 |
|---|---|
| **Read** | プロジェクト内の任意のファイルを読む |
| **Edit / Write** | ファイルを変更・作成する |
| **Bash** | シェルコマンドを実行する |
| **Glob / Grep** | コードベース全体を検索する |
| **WebSearch / WebFetch** | オンラインで情報を調べる |
| **Task** | サブエージェントを起動する |

!!! info "拡張ツール（MCP）"
    MCP（Model Context Protocol）は、エージェント本体を変更することなく、コーディングエージェントに新しいツールを追加するための標準的な方法です。

    - **GitHub MCP** — Issue の閲覧、PR の作成
    - **Atlassian MCP** — Jira、Confluence
    - **Slack MCP** — チャンネルの閲覧、メッセージの投稿
    - **カスタム UiPath MCP** — Orchestrator や Maestro の呼び出し

## スキルの実際

スキルは 1 つのフォルダーです。`.claude/skills/`（または同等の場所）に置かれ、中に `SKILL.md` が入っています。

| 特性 | 意味 |
|---|---|
| **自動的に検出される** | エージェントは各 `SKILL.md` の description を読みます。あなたのプロンプトと合致したときに、必要に応じてスキル全体を読み込みます。 |
| **テキストだけではない** | スキルには、リファレンス文書、コードパターン、補助スクリプト、さらにはエージェントが実行できるコンパイル済みバイナリまで同梱できます。 |
| **権限が限定される** | スキルは、使用を許可されたツールを宣言します。Bash へのアクセスも細かく制御できます。 |

### SKILL.md ファイルの中身

どのスキルも、1 つの `SKILL.md` ファイルを中心に構成されています。実際の例を見てみましょう。

```yaml
---
name: uipath-coded-agents
description: Scaffold, build, run, evaluate, and deploy UiPath coded agents...
allowed-tools: [Read, Edit, Bash(uip:*), Bash(uipath:*)]
---

# How to build a UiPath coded agent

When the user asks for a new coded agent:

1. Run `uipath new --framework langgraph`
2. Create agent.py following the pattern in references/
3. Add an evals/ folder with at least 5 test cases
4. Run `uipath eval` before deploying

## References
- references/sdk-methods.md
- references/langgraph-patterns.md
```

このファイルは 4 つのパートで構成されています。

| パート | 役割 |
|---|---|
| **フロントマター** | スキルの名前、説明、使用を許可するツールを宣言します。 |
| **ディスカバリープロンプト** | `description` フィールドが、あなたの依頼と照合される部分です。ここでマッチすることでスキルが自動的に読み込まれます。 |
| **手順（Instructions）** | ファイルの本文。スキルが有効なときにエージェントが従う、ステップバイステップのプロンプトです。 |
| **リファレンス（References）** | より深いコンテキスト（API ドキュメント、コードパターン、サンプルプロジェクトなど）としてエージェントが読めるファイルへのパスです。 |

## この構図における UiPath の位置づけ

UiPath は Claude Code 向けのプラグインを提供しています。スキル、フック、リファレンスがまとめられており、UiPath 製品に関するドメイン知識を最初からエージェントに与えられます。

```bash
npm -g install @uipath/cli
uip skills install
```

プラグインには次の 3 つが含まれます。

| 内容 | 詳細 |
|---|---|
| **10 以上のスキル** | UiPath の各製品に対応したドメイン知識: `uipath-agents`、`uipath-coded-apps`、`uipath-rpa`、`uipath-maestro-flow`、`uipath-platform`、`uipath-test` など。 |
| **1 つのサブエージェント** | `uipath-project-discovery-agent` — UiPath プロジェクトに最初に触れたときに自動実行され、エージェント向けのコンテキストを構築します。 |
| **フックとリファレンス** | セッション開始時のガイド、アクティビティのドキュメント、安全な読み取り専用コマンドの許可リストなど。 |

## UiPath スキルカタログ

このプラグインには、UiPath プラットフォームのあらゆる領域に対応するスキルが含まれています。本演習のラボでは、そのうち 3 つを使用します。

| スキル | 説明 |
|---|---|
| **`uipath-agents`** | コーデッドエージェント（LangGraph、LlamaIndex、OpenAI Agents）のスキャフォールド、ビルド、実行、評価、デプロイ |
| **`uipath-rpa`** | Studio Desktop 向けの RPA ワークフロー（XAML）を、まず調査するアプローチで生成・編集 |
| **`uipath-coded-apps`** | TypeScript + React アプリの Studio Web へのプッシュ／プル、Orchestrator へのパック＆パブリッシュ |
| `uipath-solution` | ソリューションの作成とデプロイ |
| `uipath-maestro-flow` | .flow JSON 形式を使った UiPath Flow プロジェクトの作成、検証、デバッグ |
| `uipath-platform` | 認証、Orchestrator の管理、ソリューションのライフサイクル、Integration Service、CLI ツール |
| `uipath-test` | UiPath プロジェクト向けの自動テストスイートの生成、実行、保守 |

!!! tip "本演習で使うスキル"
    太字の 3 つ（`uipath-agents`、`uipath-rpa`、`uipath-coded-apps`）が、ローン審査パイプラインの構築に使うスキルです。
