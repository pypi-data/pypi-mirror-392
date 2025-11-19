from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get
import base64


class FreshdeskChecker(Provider):
    name = "freshdesk"
    description = "Validate FreshDesk API key + user + domain"
    args = [
        ("-u", "--user", "FreshDesk user email"),
        ("-k", "--api-key", "FreshDesk API key"),
        ("-d", "--domain", "FreshDesk domain (example: company.freshdesk.com)"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        domain = args.domain
        if not domain:
            return False, "domain required"
        auth = base64.b64encode(f"{args.user}:{args.api_key}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}
        url = f"https://{domain}.freshdesk.com/api/v2/groups/1"
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid FreshDesk API key"
        if code == 403:
            return False, "Forbidden (check credentials and endpoint)"
        return False, f"Invalid FreshDesk key (status {code})"
