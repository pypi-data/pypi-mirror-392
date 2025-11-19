from __future__ import annotations
from typing import Tuple, Dict, Any
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class PendoChecker(Provider):
    name = "pendo"
    description = "Validate Pendo integration key"
    args = [("-k", "--key", "Pendo Integration Key")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        key = args.key

        headers: Dict[str, Any] = {
            "content-type": "application/json",
            "x-pendo-integration-key": key,
        }

        endpoints = [
            "https://app.pendo.io/api/v1/feature",
            "https://app.pendo.io/api/v1/metadata/schema/account",
        ]

        valid_hit = False

        for url in endpoints:
            code, body = http_get(url, headers=headers)

            if code is None:
                return False, f"Request error: {body}"

            # Valid:
            #   - HTTP 200
            #   - body is JSON list or JSON object
            if code == 200 and ("[" in body or "{" in body):
                valid_hit = True
                break

            # Invalid keys often return:
            # {"message":"Authentication Failed"}
            if "authentication" in body.lower() or "failed" in body.lower():
                continue

        if valid_hit:
            return True, "Valid Pendo Integration Key"

        return False, "Invalid Pendo Integration Key"
