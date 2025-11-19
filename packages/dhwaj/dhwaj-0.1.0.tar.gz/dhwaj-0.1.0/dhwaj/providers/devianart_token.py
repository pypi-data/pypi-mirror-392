from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post


class DeviantArtAccessTokenChecker(Provider):
    name = "deviantart-token"
    description = "Validate DeviantArt Access Token"
    args = [("-t", "--token", "DeviantArt Access Token")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        token = args.token

        url = "https://www.deviantart.com/api/v1/oauth2/placebo"
        data = {"access_token": token}

        code, body = http_post(url, data=data)

        if code is None:
            return False, f"Request error: {body}"

        # Valid response example:
        # {"status":"success"}
        if '"status"' in body.lower() and "success" in body.lower():
            return True, "Valid DeviantArt Access Token"

        # Invalid responses contain error info:
        # {"error":"invalid_token"}
        if '"error"' in body.lower():
            return False, "Invalid DeviantArt Access Token"

        return False, f"Unknown response (status {code})"
