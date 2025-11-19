from __future__ import annotations
from typing import Tuple, Dict
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class AppCenterChecker(Provider):
    name = "appcenter"
    description = "Validate Microsoft App Center API Token"
    args = [("-k", "--key", "App Center API Token")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = "https://api.appcenter.ms/v0.1/apps"
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "X-Api-Token": args.key,
        }
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid App Center API token"
        return False, f"Invalid App Center token (status {code})"
