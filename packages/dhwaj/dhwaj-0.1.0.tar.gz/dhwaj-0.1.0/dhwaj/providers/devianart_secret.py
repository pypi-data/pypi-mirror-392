from __future__ import annotations
from typing import Tuple, Dict
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post


class DeviantArtSecretChecker(Provider):
    name = "deviantart-secret"
    description = "Validate DeviantArt Client ID + Secret"
    args = [
        ("-id", "--client_id", "DeviantArt Client ID"),
        ("-s", "--client_secret", "DeviantArt Client Secret"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        client_id = args.client_id
        client_secret = args.client_secret

        url = "https://www.deviantart.com/oauth2/token"

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        data: Dict[str, str] = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }

        code, body = http_post(url, headers=headers, data=data)

        if code is None:
            return False, f"Request error: {body}"

        # Valid example:
        # {"access_token":"...", "token_type":"bearer", "expires_in":3600}
        if '"access_token"' in body.lower():
            return True, "Valid DeviantArt Client ID + Secret"

        # Invalid example:
        # {"error_description":"Invalid client","error":"invalid_client"}
        if '"invalid' in body.lower() or '"error"' in body.lower():
            return False, "Invalid DeviantArt Credentials"

        return False, f"Unknown response (status {code})"
