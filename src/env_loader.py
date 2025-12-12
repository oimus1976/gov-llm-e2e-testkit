# src/env_loader.py
# env_loader v0.2.3 ― Design_env_v0.2.3 準拠
#
# - env.yaml（構造の単一ソース）
# - .env / .env.<profile>（Secrets）
# - OS環境変数（最優先 & 権威）
#
# profile_config, options の 2 dict を返す。
# CI / LGWAN / INTERNET / dev の全モードと整合。
#
# NOTE:
# - Design_env_v0.2.3 は「Clarifying Update」であり、
#   基本動作は v0.2 と互換だが、以下の拘束が強化されている：
#   - Structure Integrity Rule（スキーマ不変）
#   - AI Prohibitions（schema drift / key rename 禁止）
#   - Minimal Binding Example への完全準拠

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml
from dotenv import load_dotenv


# ---------------------------------------------------------
# MissingSecretError（Design_env_v0.2.3 による拘束）
# ---------------------------------------------------------
class MissingSecretError(EnvironmentError):
    """
    env.yaml 内のプレースホルダ ${VAR_NAME} に対応する Secrets が
    .env / .env.<profile> / OS環境変数 のいずれにも存在しない場合に発生する。

    - Design_env_v0.2.3 / Debugging_Principles v0.2 に基づき、
      「どの環境変数が」「どの profile / path に対して」不足しているかを
      一次情報として明示する。
    """

    pass


# ---------------------------------------------------------
# .env / .env.<profile> の読み込み（Precedence ルール）
# ---------------------------------------------------------
def _load_dotenv_for_profile(profile: str) -> None:
    """
    Design_env_v0.2.3 の Precedence Rule に従い、
    override=False でロードする。

    Precedence（権威の優先順位）は次の通り：
        1. OS 環境変数（最優先 / 既存値は保持）
        2. .env
        3. .env.<profile>

    load_dotenv(..., override=False) により、
    既に OS に設定されている値は .env 系では上書きされない。
    """

    # 1. 共通 .env
    load_dotenv(dotenv_path=Path(".env"), override=False)

    # 2. プロファイル別 .env.<profile>
    profile_env = Path(f".env.{profile}")
    load_dotenv(dotenv_path=profile_env, override=False)


# ---------------------------------------------------------
# プレースホルダ解決（再帰版）
# ---------------------------------------------------------
def _resolve_placeholders_in_obj(
    profile_name: str,
    obj: Any,
    path: str = "",
) -> Any:
    """
    任意の Python オブジェクト内に含まれる `${VAR}` 形式の文字列を、
    OS 環境変数から解決する。

    - 文字列については「完全一致 `${VAR}`」のみ解決対象とし、
      部分文字列の置換は行わない（設計書の想定に忠実）。
    - dict / list / ネスト構造にも再帰的に対応する。
    - スキーマ不変ルールに従い、key の追加・削除・rename は一切行わない。
      （構造はそのままに「値だけ」を差し替える）
    """

    # `${VAR}` 完全一致のみ対象
    if isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
        env_key = obj.strip("${}")
        env_val = os.getenv(env_key)

        if env_val is None:
            # Debugging_Principles v0.2 に基づき、
            # どの変数が / どの profile / どの path で不足したかを明示する。
            location = path or "<root>"
            raise MissingSecretError(
                f"Missing required environment variable '{env_key}' "
                f"for profile '{profile_name}' at '{location}'. "
                "Checked sources: os.environ, .env, .env.<profile>."
            )

        return env_val

    # dict: key はそのまま、値だけ再帰的に解決
    if isinstance(obj, dict):
        resolved: Dict[str, Any] = {}
        for key, value in obj.items():
            child_path = f"{path}.{key}" if path else key
            resolved[key] = _resolve_placeholders_in_obj(
                profile_name, value, child_path
            )
        return resolved

    # list / tuple: 長さ・順序は維持したまま要素を解決
    if isinstance(obj, list):
        resolved_list = []
        for idx, item in enumerate(obj):
            child_path = f"{path}[{idx}]"
            resolved_list.append(
                _resolve_placeholders_in_obj(profile_name, item, child_path)
            )
        return resolved_list

    if isinstance(obj, tuple):
        resolved_items = []
        for idx, item in enumerate(obj):
            child_path = f"{path}[{idx}]"
            resolved_items.append(
                _resolve_placeholders_in_obj(profile_name, item, child_path)
            )
        return tuple(resolved_items)

    # それ以外の型はそのまま返す（構造不変）
    return obj


def _resolve_placeholders(profile_name: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
    """
    後方互換のためのラッパー。
    v0.2 系では「フラットな dict 前提」だったが、
    v0.2.3 ではネスト構造および list/tuple も解決対象とする。

    引数 cfg は dict を想定するが、内部要素は任意にネストしてよい。
    """
    if cfg is None:
        return {}

    if not isinstance(cfg, dict):
        raise TypeError(
            f"_resolve_placeholders expects dict, got {type(cfg)!r} for profile '{profile_name}'"
        )

    return _resolve_placeholders_in_obj(profile_name, cfg, path="")


# ---------------------------------------------------------
# load_env（v0.2.3）本体
# ---------------------------------------------------------
def load_env(env_path: str = "env.yaml") -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    env.yaml + .env + .env.<profile> + OS環境変数 の 3 レイヤを統合し、
    profile_config と options を生成する。

    Design_env_v0.2.3 における拘束：

    - env.yaml が唯一の構成ソース（Single Source of Truth）
    - profile / options のスキーマは実行時に変更してはならない
      （Structure Integrity Rule）
    - CI / LGWAN / INTERNET / dev などの実行モードを
      env_loader から“検知”してはならない
      （CI は単に env の提供元であり、ロジックは埋め込まない）
    - fallback profile の自動切替は禁止
    - MissingSecretError / ValueError 以外の暗黙 fallback は禁止

    Returns:
        profile_config: dict
        options: dict
    """

    # ---------------------------------------------
    # 1. env.yaml の読込
    # ---------------------------------------------
    env_file = Path(env_path)
    if not env_file.exists():
        raise FileNotFoundError(f"env.yaml not found at: {env_path}")

    with env_file.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    # ---------------------------------------------
    # 2. プロファイル決定
    #    ENV_PROFILE > env.yaml["profile"]
    # ---------------------------------------------
    selected = os.getenv("ENV_PROFILE", cfg.get("profile"))
    profiles = cfg.get("profiles", {})

    if selected not in profiles:
        # 自動 fallback は禁止（Design_env_v0.2.3）
        raise ValueError(f"Invalid profile '{selected}' in ENV_PROFILE or env.yaml")

    profile_cfg = profiles[selected]

    # ---------------------------------------------
    # 3. .env / .env.<profile> のロード
    # ---------------------------------------------
    _load_dotenv_for_profile(selected)

    # ---------------------------------------------
    # 4. プレースホルダ（${VAR}）解決
    #    - profile_cfg: 選択プロファイル
    #    - options:     env.yaml["options"]
    # ---------------------------------------------
    resolved_profile_cfg = _resolve_placeholders(selected, profile_cfg)

    options_cfg = cfg.get("options", {}) or {}
    # options も同じルールで解決するが、
    # profile 名は "options" として区別しておく
    resolved_options_cfg = _resolve_placeholders("options", options_cfg)

    # ---------------------------------------------
    # 5. スキーマ不変ルール確認（最低限）
    #
    #   - key 集合は変わらない前提で実装しているため、
    #     コード側では敢えて assert などは置かない。
    #     （Schema Drift の検知はテスト側で行う）
    # ---------------------------------------------
    # ※ここでは構造に触らず、そのまま返すことで
    #   Design_env_v0.2.3 の Structure Integrity Rule に従う。

    return resolved_profile_cfg, resolved_options_cfg
