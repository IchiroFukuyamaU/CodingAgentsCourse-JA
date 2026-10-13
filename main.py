"""
MkDocs-macros モジュール — 演習環境の値をページに注入します。

なぜこれがあるのか
------------------
組織名・テナント名・フォルダー名などは利用者ごとに違います。
本文に直書きすると、別のテナントで使うときに全ページを書き換えることになります。
そこでページ側では変数を参照し、値はこのファイルだけで管理します。

    Orchestrator の **{{ practice_folder }}** フォルダーを開きます。

環境はビルド時に COURSE_ENV で切り替えます。

    COURSE_ENV=staging mkdocs serve     # 検証環境（既定）
    COURSE_ENV=prod    mkdocs build     # 顧客提供環境

自分のテナントで使うには
------------------------
下の ENVIRONMENTS の値を書き換えるだけです。本文側は変更不要です。
"""

import os

ENVIRONMENTS = {
    # 検証環境（2026-10 に全レッスンの動作を確認した環境）
    "staging": {
        "cloud_host": "https://staging.uipath.com",
        "org_name": "fukuyamasandboxenv",
        "training_tenant": "DefaultTenant",
        "env_label": "検証環境（staging）",
    },
    # 顧客提供環境。公開前にここを自社の値へ差し替えてください。
    "prod": {
        "cloud_host": "https://cloud.uipath.com",
        "org_name": "CHANGE-ME-org",
        "training_tenant": "CHANGE-ME-tenant",
        "env_label": "本番環境（cloud）",
    },
}

# 環境によらず共通の値。演習で作成するリソースの名前です。
COMMON = {
    "practice_folder": "CodingAgentsWorkshop",
    "storage_bucket": "LoanUnderwriting",
    "uibank_api": "https://uibank-api.uipath.com",
    "uibank_swagger": "https://uibank-api.uipath.com/explorer/swagger.json",
    # 学習者からの問い合わせ窓口。自社の窓口に差し替えてください。
    "contact": "（自社の問い合わせ窓口に差し替えてください）",
}


def define_env(env):
    profile = os.getenv("COURSE_ENV", "staging").lower()
    cfg = ENVIRONMENTS.get(profile, ENVIRONMENTS["staging"])

    for key, value in cfg.items():
        env.variables[key] = value
    for key, value in COMMON.items():
        env.variables[key] = value

    env.variables["course_env"] = profile

    # 組み立て値 — 本文で何度も使うため、ここで作っておきます。
    env.variables["training_url"] = f"{cfg['cloud_host']}/{cfg['org_name']}"
    env.variables["login_command"] = (
        f"uip login --authority {cfg['cloud_host']}/{cfg['org_name']} "
        f"-t {cfg['training_tenant']}"
    )
