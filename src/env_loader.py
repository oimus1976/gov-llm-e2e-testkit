# src/env_loader.py
# env_loader v0.2  ― Design_env_v0.2.md 準拠
#
# - env.yaml（構造）
# - .env / .env.<profile>（Secrets）
# - OS環境変数（最優先）
#
# profile_config, options の 2 dict を返す。
# CI / LGWAN / INTERNET / dev の全モードと整合。


from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml
from dotenv import load_dotenv


# ---------------------------------------------------------
# MissingSecretError（v0.2 新設）
# ---------------------------------------------------------
class MissingSecretError(EnvironmentError):
    """env.yaml のプレースホルダに対応する Secrets が
    .env / .env.<profile> / OS環境変数 のいずれにも存在しない場合に発生する。
    """
    pass


# ---------------------------------------------------------
# .env / .env.<profile> の読み込み
# ---------------------------------------------------------
def _load_dotenv_for_profile(profile: str) -> None:
    """
    Design_env_v0.2 の「優先順位ルール（Precedence）」に従い、
    override=False でロードする。

    1. .env （共通）
    2. .env.<profile>
    """
    # 1. 共通 .env
    load_dotenv(dotenv_path=Path(".env"), override=False)

    # 2. プロファイル別
    profile_env = Path(f".env.{profile}")
    load_dotenv(dotenv_path=profile_env, override=False)


# ---------------------------------------------------------
# プレースホルダ（${VARNAME}）の解決
# ---------------------------------------------------------
def _resolve_placeholders(profile_name: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
    """
    env.yaml の profile_cfg に含まれる ${VAR} を OS環境変数で解決する。
    （.env の読み込みは load_env() の前段で済ませる）
    """
    resolved = {}

    for key, value in cfg.items():
        # 文字列のみ置換対象
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_key = value.strip("${}")
            env_val = os.getenv(env_key)

            if env_val is None:
                # MissingSecretError を送出
                raise MissingSecretError(
                    f"Environment variable '{env_key}' is not set "
                    f"but required by env.yaml profile '{profile_name}' "
                    f"(key: {key})"
                )

            resolved[key] = env_val
        else:
            # 置換不要な値はそのまま
            resolved[key] = value

    return resolved


# ---------------------------------------------------------
# load_env（v0.2）本体
# ---------------------------------------------------------
def load_env(env_path: str = "env.yaml") -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    env.yaml + .env + .env.<profile> + OS環境変数の
    3レイヤを統合し、profile_config と options を生成する。

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
        cfg = yaml.safe_load(f)

    # ---------------------------------------------
    # 2. プロファイル決定
    #    ENV_PROFILE > env.yaml["profile"]
    # ---------------------------------------------
    selected = os.getenv("ENV_PROFILE", cfg.get("profile"))
    profiles = cfg.get("profiles", {})
    if selected not in profiles:
        raise ValueError(f"Invalid profile '{selected}' in ENV_PROFILE or env.yaml")

    profile_cfg = profiles[selected]

    # ---------------------------------------------
    # 3. .env / .env.<profile> のロード
    # ---------------------------------------------
    _load_dotenv_for_profile(selected)

    # ---------------------------------------------
    # 4. プレースホルダ（${VAR}）解決
    # ---------------------------------------------
    resolved_profile_cfg = _resolve_placeholders(selected, profile_cfg)

    # ---------------------------------------------
    # 5. options セクション
    # ---------------------------------------------
    options = cfg.get("options", {})

    return resolved_profile_cfg, options
