from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class SauceLabsChecker(Provider):
    name = "saucelabs"
    description = "Validate SauceLabs username + access key"
    args = [
        ("-u", "--username", "SauceLabs username"),
        ("-k", "--access-key", "SauceLabs access key"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        username = args.username
        access_key = args.access_key

        url = f"https://saucelabs.com/rest/v1/users/{username}"

        # Basic auth through headers manually (requests supports it directly,
        # but since we must use http_get wrapper, we set Authorization header ourselves)
        import base64

        token = base64.b64encode(f"{username}:{access_key}".encode()).decode()
        headers = {"Authorization": f"Basic {token}"}

        code, body = http_get(url, headers=headers)

        # Valid credentials → 200 + user JSON
        if code == 200 and '"error"' not in str(body).lower():
            return True, "Valid SauceLabs Username + Access Key"

        return False, f"Invalid SauceLabs credentials (status {code})"
