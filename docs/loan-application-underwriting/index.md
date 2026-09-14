# ローン審査（Studio RPA・コーデッドエージェント・コーデッドアプリ・Maestro）
**UiPath のコーディングスキルを使って、UiBank 向けのコードファーストな与信審査パイプラインを丸ごと構築します**

## 概要

UiBank には毎日ローンの申込が届きます。1 件ごとに与信審査（収入の確認、支出の分析、債務所得比率の算出）を行ってからでないと、ローン担当者は判断を下せません。これを手作業で行うと時間がかかり、判断がぶれ、件数の増加にも対応できません。

この演習では、この課題にコードファーストのアプローチで取り組みます。ローコードのワークフローを設定する代わりに、作りたいものを平易な言葉で説明すると、UiPath スキルを備えたコーディングエージェントが各コンポーネントを生成してくれます。どういうときにコードがドラッグ＆ドロップに勝るのか、そしてなぜそうなるのかを実感できるはずです。

構築する順番は、まず **コーデッドエージェント**、次に **ローン担当者用アプリ**、続いてそれらをつなぐ **Maestro フロー**、最後にプロセス全体を駆動する **RPA ワークフロー** です。各レッスンは単体で完結しており、最後にはすべてが連携して動きます。

ユースケースは次のとおりです。ローン申込者の CSV を 1 行ずつ処理します。申込者ごとに、RPA が UiBank API にローン申込を送信し、返ってきたローン ID を使って即座に Maestro プロセスを開始します。Maestro は AI による与信審査を実行し、低リスクの申込は自動承認に回し、中・高リスクの申込はローン担当者のレビューに送ります。

## 構築するもの

4 つのコンポーネントを、次の順序で構築します。

1. **コーデッドエージェント（Coded Agent）** — `loan_id` を受け取り、UiBank API を呼び出して見積を検証し市場データを取得したうえで、財務指標を計算し、LLM を使ってクレジットスコア・リスクバンド・審査サマリーを生成する Python / LangGraph エージェント
2. **ローン担当者用アプリ（Loan Officer App）** — AI の審査結果をローン担当者に提示し、承認（Approve）または却下（Reject）の判断を受け取る React の Coded Action App
3. **Maestro フロー（Maestro Flow）** — エージェントを呼び出し、低リスクの結果を自動承認し、中・高リスクの案件ではローン担当者用アプリを開く UiPath Flow プロセス
4. **RPA ワークフロー（RPA Workflow）** — `loan-applications.csv` を読み込み、各行を UiBank API に送信し、受理された申込ごとに Maestro Flow プロセスを開始する Studio の XAML ワークフロー

<div style="font-family: sans-serif; max-width: 680px; margin: 2rem auto;">

  <div style="text-align: center; margin-bottom: 8px;">
    <span style="display: inline-block; background: #f5f5f5; border: 2px dashed #bdbdbd; border-radius: 8px; padding: 8px 24px; font-size: 13px; color: #616161; font-family: monospace;">📄 loan-applications.csv</span>
  </div>

  <div style="text-align: center; color: #bdbdbd; font-size: 20px; margin: 4px 0;">↓</div>

  <div style="background: #e8eaf6; border: 2px solid #3f51b5; border-radius: 10px; padding: 14px 18px; margin-bottom: 8px;">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
      <div>
        <div style="font-weight: 700; color: #283593; font-size: 14px;">Studio RPA · LoanApplicationDispatcher</div>
        <div style="font-size: 12px; color: #5c6bc0; margin-top: 6px;">各行ごとに: <code style="background: #c5cae9; padding: 1px 4px; border-radius: 3px; font-size: 11px;">POST /api/quotes/newquote</code> → UiBank API</div>
      </div>
      <span style="background: #3f51b5; color: white; border-radius: 4px; padding: 3px 8px; font-size: 11px; white-space: nowrap; margin-left: 12px;">uipath-rpa</span>
    </div>
  </div>

  <div style="text-align: center; color: #bdbdbd; font-size: 20px; margin: 4px 0;">↓</div>

  <div style="text-align: center; margin-bottom: 8px;">
    <span style="background: #fff8e1; border: 1.5px solid #f9a825; border-radius: 6px; padding: 4px 16px; font-size: 12px; color: #f57f17;">◇ &nbsp;accepted == True ?</span>
  </div>

  <div style="display: flex; gap: 12px; margin-bottom: 8px;">
    <div style="flex: 1; text-align: center;">
      <div style="font-size: 11px; color: #888; margin-bottom: 4px;">いいえ</div>
      <div style="background: #ffebee; border: 1px solid #ef9a9a; border-radius: 6px; padding: 6px; font-size: 11px; color: #c62828;">results.csv に "Failed" を書き込む</div>
    </div>
    <div style="flex: 1; text-align: center;">
      <div style="font-size: 11px; color: #888; margin-bottom: 4px;">はい</div>
      <div style="background: #e8f5e9; border: 1px solid #a5d6a7; border-radius: 6px; padding: 6px; font-size: 11px; color: #2e7d32;"><code style="font-size: 10px; background: #c8e6c9; padding: 1px 3px; border-radius: 2px;">loan_id</code> を渡して Maestro Flow を開始</div>
    </div>
  </div>

  <div style="text-align: center; color: #bdbdbd; font-size: 20px; margin: 4px 0;">↓</div>

  <div style="background: #fff3e0; border: 2px solid #e65100; border-radius: 10px; padding: 14px 18px;">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
      <div style="font-weight: 700; color: #bf360c; font-size: 14px;">Maestro Flow · LoanUnderwritingProcess</div>
      <span style="background: #e65100; color: white; border-radius: 4px; padding: 3px 8px; font-size: 11px; white-space: nowrap; margin-left: 12px;">uipath-maestro-flow</span>
    </div>

    <div style="background: #f3e5f5; border: 2px solid #7b1fa2; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px;">
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <div>
          <div style="font-weight: 700; color: #4a148c; font-size: 12px;">Coded Agent · LoanUnderwritingAgent</div>
          <div style="font-size: 11px; color: #8e24aa; margin-top: 4px;">3 つの UiBank API ツールを呼び出し、<code style="background: #e1bee7; padding: 1px 3px; border-radius: 2px; font-size: 10px;">risk_band</code> · <code style="background: #e1bee7; padding: 1px 3px; border-radius: 2px; font-size: 10px;">credit_score</code> · <code style="background: #e1bee7; padding: 1px 3px; border-radius: 2px; font-size: 10px;">assessment_summary</code> を返す</div>
        </div>
        <span style="background: #7b1fa2; color: white; border-radius: 4px; padding: 2px 6px; font-size: 10px; white-space: nowrap; margin-left: 8px;">uipath-agents</span>
      </div>
    </div>

    <div style="text-align: center; margin-bottom: 12px;">
      <span style="background: #ffe0b2; border: 1.5px solid #e65100; border-radius: 6px; padding: 4px 16px; font-size: 12px; color: #bf360c;">◇ &nbsp;risk_band == "Low" ?</span>
    </div>

    <div style="display: flex; gap: 16px;">
      <div style="flex: 1; text-align: center;">
        <div style="font-size: 11px; color: #888; margin-bottom: 6px;">はい</div>
        <div style="background: #e8f5e9; border: 2px solid #388e3c; border-radius: 8px; padding: 12px; font-size: 13px; font-weight: 600; color: #1b5e20;">✓ 自動承認</div>
      </div>
      <div style="flex: 2;">
        <div style="font-size: 11px; color: #888; margin-bottom: 6px; text-align: center;">いいえ（Medium / High）</div>
        <div style="background: #e0f2f1; border: 2px solid #00796b; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <div style="font-weight: 700; color: #004d40; font-size: 12px;">Coded App · loan-officer-dashboard</div>
              <div style="font-size: 11px; color: #00796b; margin-top: 3px;">ローン担当者がレビューして判断を送信</div>
            </div>
            <span style="background: #00796b; color: white; border-radius: 4px; padding: 2px 6px; font-size: 10px; white-space: nowrap; margin-left: 8px;">uipath-coded-apps</span>
          </div>
        </div>
        <div style="text-align: center; margin-bottom: 8px;">
          <span style="background: #ffe0b2; border: 1.5px solid #e65100; border-radius: 6px; padding: 4px 12px; font-size: 11px; color: #bf360c;">◇ &nbsp;officer_decision == "Approve" ?</span>
        </div>
        <div style="display: flex; gap: 8px;">
          <div style="flex: 1; text-align: center;">
            <div style="font-size: 10px; color: #888; margin-bottom: 4px;">はい</div>
            <div style="background: #e8f5e9; border: 2px solid #388e3c; border-radius: 8px; padding: 8px; font-size: 12px; font-weight: 600; color: #1b5e20;">✓ 承認</div>
          </div>
          <div style="flex: 1; text-align: center;">
            <div style="font-size: 10px; color: #888; margin-bottom: 4px;">いいえ</div>
            <div style="background: #ffebee; border: 2px solid #c62828; border-radius: 8px; padding: 8px; font-size: 12px; font-weight: 600; color: #b71c1c;">✗ 却下</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div style="text-align: center; color: #bdbdbd; font-size: 20px; margin: 4px 0;">↓</div>

  <div style="text-align: center; margin-bottom: 8px;">
    <div style="display: inline-block; background: #e8eaf6; border: 2px solid #3f51b5; border-radius: 8px; padding: 8px 20px; font-size: 12px; color: #283593;">
      <strong>RPA</strong> · 結果を <code style="background: #c5cae9; padding: 1px 4px; border-radius: 3px; font-size: 11px;">results.csv</code> に書き込み → <strong>LoanUnderwriting</strong> ストレージバケットにアップロード
    </div>
  </div>

</div>

## はじめる前に

| | |
| ---: | :--- |
| [**コーディングエージェントとは？**](what-is-a-coding-agent.md) | 全体像、ツール、スキル、そして UiPath がどこに位置づくのかを理解する |
| [**インストールガイド**](installation-guides.md) | Node.js、Python、.NET SDK、UiPath Studio、Git、コーディングエージェントをインストールする |
| [**UiPath スキルのインストール**](install-skills.md) | UiPath CLI をインストールして認証し、スキルをコーディングエージェントに読み込む |

## ステップ

| ステップ | 内容 |
| ---: | :--- |
| [**1. AI による与信審査**](1-underwriting-agent.md) | `uipath-agents` スキルを使い、申込を分析して構造化された与信審査結果を生成する Python / LangGraph エージェントを構築します |
| [**2. ローン担当者レビュー用ダッシュボード**](2-loan-officer-app.md) | `uipath-coded-apps` スキルを使い、ローン担当者が AI の審査結果をレビューして申込を承認・却下するための React 製 Coded Action App を構築します |
| [**3. Maestro Flow によるオーケストレーション**](3-maestro-flow.md) | `uipath-maestro-flow` スキルを使い、コーデッドエージェントとローン担当者用ダッシュボードを、リスクバンドによる条件分岐を備えた Maestro プロセスに組み込みます |
| [**4. 申込受付とデータ補完**](4-intake-enrichment.md) | `uipath-rpa` スキルを使い、申込を UiBank に送信して結果を CSV に書き出す Studio の XAML ワークフローを構築します |

## 必要なもの

- インストール済みのコーディングエージェント（Claude Code、Codex CLI、Gemini CLI など）
- インストール済みの `uip` CLI（`uip --version` で 1.195.1 以降が表示されること）
- Node.js LTS（UiPath CLI と React アプリ用）
- Python 3.10 以降（コーデッドエージェント用）
- ローカルにインストールされた UiPath Studio（生成された XAML を開いて実行するため）

!!! tip "トレーニング環境"
    この演習では **[{{ training_url }}]({{ training_url }})** にログインし、テナント **{{ training_tenant }}** を使用してください。
