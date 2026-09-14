# インストールガイド
ワークショップを始める前に、必要なツールをインストールします。

## 前提条件

本番のセットアップに入る前に、以下がインストールされていることを確認してください。

**Node.js（LTS）** — UiPath CLI と React アプリのビルドに必要です。

1. **[nodejs.org](https://nodejs.org)** から LTS 版をダウンロードします
2. `node --version` と `npm --version` で確認します

!!! tip "npm のバージョンは 11.x.x である必要があります"
    `npm --version` が別のバージョンを返す場合は、アップグレードしてください。

    === "Windows"
        ```bash
        npm install --global npm@11
        ```

    === "Mac"
        ```bash
        npm install -g npm@11
        ```

**Python 3.10 以降** — コーデッドな与信審査エージェントに必要です。

1. **[python.org/downloads](https://www.python.org/downloads/)** からダウンロードします。Windows の場合はインストール時に **Add Python to PATH** にチェックを入れてください
2. `python --version` または `python3 --version` で確認します

**.NET SDK 8.0** — UiPath Studio のプロジェクトをビルド・実行するために必要です。

1. **[dotnet.microsoft.com/download/dotnet/8.0](https://dotnet.microsoft.com/download/dotnet/8.0)** からダウンロードします。Mac の場合は Homebrew でもインストールできます。
   ```bash
   brew install --cask dotnet-sdk
   ```
2. `dotnet --list-sdks` で確認します。出力に `8.x.x` が表示されるはずです

!!! tip "Windows — .NET が PATH に入っているか確認してください"
    インストール後に `dotnet` が認識されない場合は、PowerShell で PATH に手動で追加します。
    ```bash
    $env:Path = "C:\Program Files\dotnet;$env:Path"
    dotnet --list-sdks
    ```

**UiPath Studio** — 生成された XAML ワークフローを開き、実行し、デバッグするために必要です。現時点では Windows のみ対応で、Mac 対応は近日提供予定です。

1. **[uipath.com/start-trial](https://www.uipath.com/start-trial)** からダウンロードします
2. UiPath アカウントでサインインし、Studio が起動することを確認します

**Git** — UiPath スキルのマーケットプレイスに必要です。まず方法 1 を試し、うまくいかない場合は方法 2 を使ってください。

=== "方法 1: winget（最短）"

    1. ターミナルを開いて次を実行します。
       ```bash
       winget install --id Git.Git -e --source winget
       ```
    2. 利用規約への同意を求められたら `Y` を入力して Enter を押します。
    3. "Successfully installed" と表示されるまで待ち、ウィンドウを閉じます。

=== "方法 2: インストーラーをダウンロード"

    1. **[git-scm.com/download/win](https://git-scm.com/download/win)** にアクセスします。64 ビット版のインストーラーが自動的にダウンロードされます。
    2. ダウンロードしたファイル（例: `Git-2.xx.x-64-bit.exe`）を実行します。Windows から管理者権限を求められたら「はい」をクリックします。
    3. すべて既定値のままインストーラーを進めます。**"Adjusting your PATH environment"** の画面では、真ん中の選択肢 *"Git from the command line and also from 3rd-party software"* が選ばれていることを確認してください（これが既定値です）。
    4. 完了したら Finish をクリックします。

!!! warning "どちらの方法でも必須"
    PATH の変更は、新しく開いたウィンドウにしか反映されません。開いているターミナルをすべて閉じたうえで、新しいコマンドプロンプトを開いて確認してください。
    ```bash
    git --version
    ```
    `git version 2.45.1.windows.1` のように表示されるはずです。

## コーディングエージェントのインストール

どちらか 1 つを選んでください（両方入れても構いません）。

```bash
# Claude Code (Anthropic)
npm install -g @anthropic-ai/claude-code

# Codex CLI (OpenAI)
npm install -g @openai/codex
```

確認: `claude --version` または `codex --version`

!!! tip "Claude Code のインストールでエラーが出る場合"
    スクリプト実行権限のエラーでインストールが失敗する場合は、次を実行してください。
    ```bash
    npm config set allow-scripts=@anthropic-ai/claude-code --location=user
    ```
    そのうえで、インストールコマンドを再実行します。
    ```bash
    npm install -g @anthropic-ai/claude-code
    ```
