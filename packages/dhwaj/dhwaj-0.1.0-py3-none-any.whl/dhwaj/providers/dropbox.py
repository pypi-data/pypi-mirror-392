from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post


class DropboxChecker(Provider):
    name = "dropbox"
    description = "Validate Dropbox API token"
    args = [("-k", "--key", "Dropbox Access Token")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        headers = {
            "Authorization": f"Bearer {args.key}",
            "Content-Type": "application/json",
        }
        code, _ = http_post(
            "https://api.dropboxapi.com/2/users/get_current_account",
            headers=headers,
            json={},
        )
        if code == 200:
            return True, "Valid Dropbox token"
        if code == 401:
            return False, "Invalid Dropbox token"
        return False, f"Unknown response (status {code})"
