from __future__ import annotations
from typing import Tuple, Dict, Any
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post


class HelpScoutChecker(Provider):
    name: str = "helpscout"
    description: str = "Validate HelpScout OAuth client ID + secret"
    args = [
        ("-cid", "--client-id", "HelpScout client ID"),
        ("-cs", "--client-secret", "HelpScout client secret"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = "https://api.helpscout.net/v2/oauth2/token"

        headers: Dict[str, str] = {"Content-Type": "application/x-www-form-urlencoded"}

        data: Dict[str, Any] = {
            "grant_type": "client_credentials",
            "client_id": args.client_id,
            "client_secret": args.client_secret,
        }

        code, body = http_post(url, headers=headers, data=data)

        if code == 200 and '"access_token"' in (body or ""):
            return True, "Valid Help Scout client credentials"

        return False, f"Invalid Help Scout credentials (status {code})"
