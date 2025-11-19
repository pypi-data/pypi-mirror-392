from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get
import base64


class MailgunChecker(Provider):
    name = "mailgun"
    description = "Validate Mailgun private API key"
    args = [("-k", "--key", "Mailgun private API key")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        # Mailgun uses basic auth user: api
        auth = base64.b64encode(f"api:{args.key}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}
        url = "https://api.mailgun.net/v3/domains"
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid Mailgun API key"
        return False, f"Invalid Mailgun key (status {code})"
