from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class FacebookAccessTokenChecker(Provider):
    name = "facebook-token"
    description = "Validate Facebook user access token"
    args = [("-t", "--token", "Facebook Access Token")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        token = args.token

        url = (
            "https://developers.facebook.com/tools/debug/accesstoken/"
            f"?access_token={token}&version=v3.2"
        )

        code, body = http_get(url)

        if code is None:
            return False, f"Request error: {body}"

        # Valid token usually contains: "is_valid": true
        if '"is_valid": true' in body.lower():
            return True, "Valid Facebook Access Token"

        # Errors contain: "error", "OAuthException", etc.
        if '"is_valid": false' in body.lower() or '"error"' in body.lower():
            return False, f"Invalid Facebook Access Token (status {code})"

        return False, f"Unknown response (status {code})"
