# src/env_loader.py
import os
import yaml
from typing import Tuple, Dict, Any


def load_env(env_path: str = "env.yaml") -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    env.yaml を読み込み、profile（internet / lgwan）に応じて
    URL/USERNAME/PASSWORD/timeout などを展開した dict を返す。

    Returns:
        profile_config: dict（実行に必要な情報）
        options: dict（ログ設定などの共通オプション）
    """

    # env.yaml の読込
    with open(env_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # profile（ENV_PROFILE が優先）
    selected = os.getenv("ENV_PROFILE", cfg.get("profile", "internet"))
    if selected not in cfg.get("profiles", {}):
        raise ValueError(f"Invalid profile '{selected}' in ENV_PROFILE or env.yaml")

    profile_cfg = cfg["profiles"][selected].copy()

    # ${VARNAME} の置換
    for key in ["url", "username", "password"]:
        value = profile_cfg.get(key)
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_key = value.strip("${}")
            env_val = os.getenv(env_key)
            if env_val is None:
                raise EnvironmentError(
                    f"Environment variable '{env_key}' is not set "
                    f"but required by env.yaml profile '{selected}'"
                )
            profile_cfg[key] = env_val

    # 共通オプション
    options = cfg.get("options", {})

    return profile_cfg, options
