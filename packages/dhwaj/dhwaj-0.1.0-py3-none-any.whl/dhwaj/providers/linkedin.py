from __future__ import annotations
from typing import Tuple, Dict, Any
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post


class LinkedInChecker(Provider):
    name = "linkedin"
    description = "Validate LinkedIn OAuth client ID + secret"
    args = [
        ("-cid", "--client-id", "LinkedIn client ID"),
        ("-cs", "--client-secret", "LinkedIn client secret"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = "https://www.linkedin.com/oauth/v2/accessToken"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data: Dict[str, Any] = {
            "grant_type": "client_credentials",
            "client_id": args.client_id,
            "client_secret": args.client_secret,
        }
        code, body = http_post(url, headers=headers, data=data)
        if code == 200 and '"access_token"' in (body or ""):
            return True, "Valid LinkedIn client credentials"
        return False, f"Invalid LinkedIn credentials (status {code})"
