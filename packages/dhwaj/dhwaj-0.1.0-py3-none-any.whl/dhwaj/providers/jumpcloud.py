from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class JumpCloudChecker(Provider):
    name = "jumpcloud"
    description = "Validate JumpCloud API key (v1 or v2)"
    args = [
        ("-k", "--key", "JumpCloud API key"),
        ("--v2", "--v2", "Use V2 API instead of V1"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        if args.v2:
            url = f"https://console.jumpcloud.com/api/v2/systems/ -H 'x-api-key: {args.key}'"
            # v2 endpoint requires system id - do a safe generic check:
            url = "https://console.jumpcloud.com/api/v2/systemusers"
            headers = {"x-api-key": args.key}
            code, _ = http_get(url, headers=headers)
            if code == 200:
                return True, "Valid JumpCloud v2 API Key"
            return False, f"Invalid JumpCloud v2 key (status {code})"
        else:
            endpoints = [
                ("https://console.jumpcloud.com/api/systems", {"x-api-key": args.key}),
                (
                    "https://console.jumpcloud.com/api/systemusers",
                    {"x-api-key": args.key},
                ),
            ]
            for url, headers in endpoints:
                code, _ = http_get(url, headers=headers)
                if code == 200:
                    return True, "Valid JumpCloud API Key"
            return False, "Invalid JumpCloud API Key"
