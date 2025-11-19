from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class TwitterBearerChecker(Provider):
    name = "twitter-bearer"
    description = "Validate Twitter Bearer token"
    args = [("-t", "--token", "Twitter Bearer Token")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        token = args.token

        url = (
            "https://api.twitter.com/1.1/account_activity/all/subscriptions/count.json"
        )

        headers = {"authorization": f"Bearer {token}"}

        code, body = http_get(url, headers=headers)

        if code is None:
            return False, f"Request error: {body}"

        # Valid tokens return JSON or data like:
        # {"subscriptions_count":{...}}
        if code == 200 and "subscriptions" in body.lower():
            return True, "Valid Twitter Bearer Token"

        # Invalid = 401 unauthorized
        if code == 401 or "invalid" in body.lower() or "unauthorized" in body.lower():
            return False, "Invalid Twitter Bearer Token"

        return False, f"Unknown response (status {code})"
