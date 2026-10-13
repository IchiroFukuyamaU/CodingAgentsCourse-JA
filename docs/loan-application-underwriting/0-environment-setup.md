# 0. 演習環境を準備する

このあとのレッスンで使う土台を用意します。**所要 20 分程度です。**

作成するものは 3 つです。

| 種類 | 名前 | 用途 |
|---|---|---|
| Orchestrator フォルダー | `{{ practice_folder }}` | デプロイしたものをすべてここに配置します |
| ストレージバケット | `{{ storage_bucket }}` | レッスン4 で `results.csv` をアップロードします |
| **ソリューション** | `LoanApplicationUnderwriting` | **レッスン1・3・4 で作るプロジェクトを束ねる単位** |

!!! note "名前は変えても構いません"
    別の名前にする場合は、**以降のすべてのレッスンで読み替えてください。** 本文中の `{{ practice_folder }}` と `{{ storage_bucket }}` がそれにあたります。

---

## 1. ログインする

まずログイン状態を確認します。

```bash
uip login status --output json
```

`Status` が `Logged in` で、`Organization` と `Tenant` が演習環境のものであれば、このまま次へ進んでください。そうでなければログインします。

```bash
{{ login_command }}
```

`{{ org_name }}` と `{{ training_tenant }}` は、**ご自身の組織名・テナント名に置き換えてください。**
Automation Cloud の画面右上、または URL（`https://cloud.uipath.com/<組織名>/<テナント名>/...`）から確認できます。

ブラウザーが開くのでサインインしてください。

!!! warning "ログインは自分のターミナルで実行してください"
    `uip login` はブラウザーでの対話的なサインインが必要です。コーディングエージェントに実行させると、ブラウザーが開いたまま応答がなくなることがあります。

---

## 2. フォルダーを作成する

```bash
uip or folders create "{{ practice_folder }}" --output json
```

!!! note "名前は位置引数です"
    `--name` というオプションはありません。フォルダー名はコマンドの最後に、そのまま書きます。

次のような結果が返ります。`Key` の値は後で使うので控えておいてください。

```json
{
  "Result": "Success",
  "Code": "FolderCreated",
  "Data": {
    "Key": "b956f165-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "Id": 1248846,
    "Name": "{{ practice_folder }}"
  }
}
```

!!! tip "フォルダーキーを控えておく理由"
    多くのコマンドは `--folder-path "{{ practice_folder }}"` と**名前で**指定できますが、**一部のコマンドはキー（GUID）しか受け付けません。** 特にレッスン2 の `uip codedapp deploy` がそうです。

    あとで調べ直すこともできます。

    ```bash
    uip or folders list --all --name "{{ practice_folder }}" --output json
    ```

---

## 3. ストレージバケットを作成する

レッスン4 で使います。先に作っておきます。

```bash
uip or buckets create "{{ storage_bucket }}" --folder-path "{{ practice_folder }}" --output json
```

結果に `Identifier` と `Id` が返れば成功です。

---

## 4. ソリューションを作成する

!!! info "ソリューションとは"
    UiPath では、関連するプロジェクトを **1 つのソリューション**にまとめます。ローン審査のパイプラインは
    エージェント・アプリ・フロー・RPA の 4 つで 1 つの業務なので、本来これらは**ばらばらの成果物ではなく、
    ひとまとまり**として扱うものです。

    ソリューションにまとめると次の利点があります。

    - **Studio Web に 1 件として取り込める**（ばらばらだと 4 件に分かれます）
    - **`uip solution deploy run` で一括デプロイできる**
    - バージョンがソリューション単位でまとまる
    - **依存するリソースが明示される** — バケットやアセットなど、使う Orchestrator リソースを
      ソリューションに宣言します（レッスン4 で実際に行います）

    本コースでは **レッスン0 でソリューションを作り、各レッスンでその中にプロジェクトを足していきます。**

```bash
uip solution init "LoanApplicationUnderwriting" --output json
```

`LoanApplicationUnderwriting/` というフォルダーと、その中に `LoanApplicationUnderwriting.uipx`（ソリューションの
マニフェスト）ができます。**以降のレッスンは、このフォルダーの中で作業します。**

```bash
cd LoanApplicationUnderwriting
```

!!! warning "ローン担当者ダッシュボード（レッスン2）だけは例外です"
    Coded Action App は、**現時点ではソリューションに含めても配備先フォルダーにアプリが作られません。**
    そのためレッスン2 のアプリだけは、ソリューションの**外**に独立したプロジェクトとして作り、
    `uip codedapp deploy` で個別にデプロイします。

    理由と詳細はレッスン2 で説明します。最終的なフォルダー構成は次のようになります。

    ```
    作業フォルダー/
    ├── LoanApplicationUnderwriting/      ← ソリューション
    │   ├── LoanApplicationUnderwriting.uipx
    │   ├── LoanUnderwritingAgent/        （レッスン1）
    │   ├── LoanUnderwritingProcess/      （レッスン3）
    │   └── LoanApplicationDispatcher/    （レッスン4）
    └── loanofficerdashboard/             ← ソリューション外（レッスン2）
    ```

## 5. 確認する

両方が作成されたことを確認します。

```bash
uip or folders list --all --name "{{ practice_folder }}" --output table
uip or buckets list --folder-path "{{ practice_folder }}" --output table
```

**Orchestrator** の画面でも確認しておくと、このあとのレッスンで迷いにくくなります。

- **Orchestrator** → 左メニューの**フォルダー** に `{{ practice_folder }}` がある
- そのフォルダーを開いて **ストレージバケット** に `{{ storage_bucket }}` がある

---

## 6. 必要なツールが揃っているか確認する

`uip` CLI は、必要なツールを**初回使用時に自動でインストール**します。事前の導入作業は不要です。

現在インストールされているものを確認するには次を実行します。

```bash
uip tools list
```

!!! note "表示されていなくても問題ありません"
    `docsai` や `codedagent` が一覧に無くても、**初めて使うときに自動で導入されます。** 手動でインストールする必要はありません。

    ただし**初回は数分かかることがあります。** コマンドが返ってこなくても、しばらく待ってください。

このあとのレッスンで使うツールは次のとおりです。

| ツール | 使うレッスン |
|---|---|
| `codedagent` | 1. AI による与信審査 |
| `codedapp` | 2. ローン担当者レビュー用ダッシュボード |
| `maestro` | 3. Maestro Flow によるオーケストレーション |
| `rpa` | 4. 申込受付とデータ補完 |

---

## 準備完了です

これで、[1. AI による与信審査](1-underwriting-agent.md)に進めます。

!!! tip "やり直したくなったら"
    各レッスンは独立しています。途中で作り直したくなったら、[演習環境の片付け](../cleanup.md)で該当のリソースだけ削除して、そのレッスンからやり直せます。
