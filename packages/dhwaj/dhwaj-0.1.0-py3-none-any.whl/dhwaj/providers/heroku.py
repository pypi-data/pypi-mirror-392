from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post


class HerokuChecker(Provider):
    name = "heroku"
    description = "Validate Heroku API key (Bearer)"
    args = [("-k", "--key", "Heroku API key")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = "https://api.heroku.com/apps"
        headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer {args.key}",
        }
        code, _ = http_post(url, headers=headers)
        if code == 200:
            return True, "Valid Heroku API key"
        if code == 401:
            return False, "Invalid Heroku API key"
        return False, f"Unknown response (status {code})"
