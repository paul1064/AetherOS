#!/usr/bin/env python3
# MIT License

from __future__ import annotations

from typing import Any

import requests

from aether_core import load_config


def api_base_url() -> str:
    cfg = load_config().raw["runtime"]
    return f"http://{cfg['api_host']}:{cfg['api_port']}"


def api_get(path: str) -> dict[str, Any] | list[dict[str, Any]]:
    response = requests.get(f"{api_base_url()}{path}", timeout=30)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(f"{api_base_url()}{path}", json=payload, timeout=60)
    response.raise_for_status()
    return response.json()
