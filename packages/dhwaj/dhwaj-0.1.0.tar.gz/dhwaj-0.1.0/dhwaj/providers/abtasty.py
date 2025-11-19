from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class ABTastyChecker(Provider):
    name = "abtasty"
    description = "Validate ABTasty API key"
    args = [
        ("-k", "--key", "ABTasty API key"),
        ("-u", "--url", "ABTasty instance URL (optional)"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        # generic test: request an endpoint with header
        url = args.url or "https://api.abtasty.com/"
        headers = {"x-api-key": args.key}
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid ABTasty API key"
        return False, f"Invalid ABTasty key (status {code})"
