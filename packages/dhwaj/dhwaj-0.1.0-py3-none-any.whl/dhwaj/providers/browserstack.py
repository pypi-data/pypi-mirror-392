from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get
import base64


class BrowserStackChecker(Provider):
    name = "browserstack"
    description = "Validate BrowserStack username + access key"
    args = [
        ("-u", "--username", "BrowserStack Username"),
        ("-k", "--access-key", "BrowserStack Access Key"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        auth = base64.b64encode(f"{args.username}:{args.access_key}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}
        url = "https://api.browserstack.com/automate/plan.json"
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid BrowserStack credentials"
        return False, f"Invalid BrowserStack credentials (status {code})"
