from __future__ import annotations
from typing import Tuple, Dict
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post
import base64


class TwitterAPISecretChecker(Provider):
    name = "twitter-secret"
    description = "Validate Twitter API key + API secret"
    args = [
        ("-k", "--key", "Twitter API key"),
        ("-s", "--secret", "Twitter API secret"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        api_key = args.key
        api_secret = args.secret

        auth_str = f"{api_key}:{api_secret}".encode()
        auth_b64 = base64.b64encode(auth_str).decode()

        url = "https://api.twitter.com/oauth2/token"
        headers: Dict[str, str] = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {"grant_type": "client_credentials"}

        code, body = http_post(url, headers=headers, data=data)

        if code is None:
            return False, f"Request error: {body}"

        if '"token_type":"bearer"' in body.lower():
            return True, "Valid Twitter API Key + Secret"

        if '"errors"' in body.lower():
            return False, f"Invalid Twitter credentials (status {code})"

        return False, f"Unknown response (status {code})"
