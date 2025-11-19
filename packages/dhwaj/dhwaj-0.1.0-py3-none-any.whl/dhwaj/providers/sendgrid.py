from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class SendGridChecker(Provider):
    name = "sendgrid"
    description = "Validate SendGrid API token"
    args = [("-t", "--token", "SendGrid API token")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        token = args.token

        url = "https://api.sendgrid.com/v3/scopes"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        code, body = http_get(url, headers=headers)

        if code is None:
            return False, f"Request error: {body}"

        if code == 200 and '"scopes"' in body.lower():
            return True, "Valid SendGrid API Token"

        if code in [401, 403] or "error" in body.lower():
            return False, "Invalid SendGrid API Token"

        return False, f"Unknown response (status {code})"
