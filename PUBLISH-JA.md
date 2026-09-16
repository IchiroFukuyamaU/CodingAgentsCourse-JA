# 公開手順（GitHub Pages）

公開先リポジトリ:
**<https://github.com/UiPathPartnersJPN/CodingAgentsCourse-JA>**

公開 URL（Pages 有効化後）:
**<https://uipathpartnersjpn.github.io/CodingAgentsCourse-JA/>**

---

## ⚠ ブラウザの「Upload files」は使わないでください

GitHub の Web UI のドラッグ＆ドロップは、サブフォルダーや隠しフォルダーを取りこぼします。
実際に最初の試行では、ルート直下の 9 ファイルだけがアップロードされ、以下がすべて欠落しました。

- `docs/` — 日本語化したレッスン本文（サイトの中身そのもの）
- `.github/workflows/deploy.yml` — これが無いとビルドが一度も走りません
- `hooks/`、`Master/`、`scripts/`、`.claude/`

さらに、ソースの zip（内部に `.git` を含む 4.5 MB）が誤ってコミットされていました。
本リポジトリのコミット `518b34e` でこれらは修正済みです。

**以下のどちらかの方法で push してください。**

---

## 方法 A: GitHub Desktop（GUI・推奨）

1. [GitHub Desktop](https://desktop.github.com/) をインストールし、GitHub アカウントでサインインします
2. 配布された zip（`.git` を含むフルバージョン）を展開します
3. **File → Add local repository** で、展開した `CodingAgentsCourse-ja` フォルダーを指定します
4. 左下に未 push のコミットが表示されます。**Repository → Repository settings → Remote** を開き、
   Primary remote repository を次に設定します。

   ```
   https://github.com/UiPathPartnersJPN/CodingAgentsCourse-JA.git
   ```

5. **Push origin** をクリックします

フォルダー構成・隠しフォルダー・ファイル数をすべて正しく扱ってくれるため、Web UI より確実です。

## 方法 B: コマンドライン

```bash
cd CodingAgentsCourse-ja
git remote set-url origin https://github.com/UiPathPartnersJPN/CodingAgentsCourse-JA.git
git push origin main
```

`--force` は不要です。このリポジトリの履歴には既存の 2 コミット（`8435ef8`、`cad0aa2`）が
祖先として含まれているため、通常の push が fast-forward で通ります。

`gh` CLI を使う場合は、事前に `gh auth login` で認証しておいてください。

---

## 権限について

`UiPathPartnersJPN` は Organization です。push するには、この Organization で
**Write** 以上の権限が必要です。403 で弾かれる場合は、Organization の管理者に
権限付与を依頼してください。

---

## push 後の手順

### 1. ビルドを確認する

リポジトリの **Actions** タブを開きます。`Deploy site` というワークフローが自動で走り、
1 分ほどで完了します。緑のチェックが付くのを待ってください。

失敗する場合は **Settings → Actions → General → Workflow permissions** を確認し、
**Read and write permissions** に設定してください。

### 2. GitHub Pages を有効にする

ワークフローが成功すると `gh-pages` ブランチが作成されます。そのあとで、

1. **Settings → Pages** を開きます
2. **Source** を **Deploy from a branch** にします
3. **Branch** を `gh-pages` / `(root)` に設定して **Save** をクリックします

数分後、次の URL で公開されます。

```
https://uipathpartnersjpn.github.io/CodingAgentsCourse-JA/
```

!!! note
    Organization のプランや設定によっては、public な Pages の公開が制限されている場合があります。
    **Settings → Pages** に選択肢が出てこない場合は、Organization の設定
    （**Member privileges → Pages creation**）を確認してください。

### 3. 公開後の確認

- トップページに「トレーニング環境」の枠が表示されること
- 左のナビゲーションが日本語になっていること
- 検索ボックスで日本語のキーワード（例: 「エージェント」）が引けること

---

## ローカルでプレビューする

```bash
pip install -r requirements.txt
mkdocs serve
# http://127.0.0.1:8000 を開く
```

`main` に push するたびに、サイトは自動的に再デプロイされます。

`site_url` は GitHub Actions がリポジトリ情報から自動的に組み立てて渡すため、
`mkdocs.yml` を手で書き換える必要はありません。

---

## 原典の更新を取り込む

```bash
git remote add upstream https://github.com/uipath-practice/CodingAgentsCourse.git
git fetch upstream
git log --oneline HEAD..upstream/main        # 原典側の新しいコミットを確認
git diff HEAD..upstream/main -- docs/        # 本文の変更点を確認
```

差分を確認したうえで、必要な箇所だけを日本語版に反映してください。翻訳コミットは
1 つにまとめてあるため、`git diff` で「原典 → 日本語版」の対応が追いやすくなっています。
