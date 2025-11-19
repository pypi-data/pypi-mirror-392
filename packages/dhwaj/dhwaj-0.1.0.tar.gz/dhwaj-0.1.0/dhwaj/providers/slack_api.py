from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post


class SlackAPITokenChecker(Provider):
    name = "slack-token"
    description = "Validate Slack API token"
    args = [("-t", "--token", "Slack token (xoxb/xoxp)")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        token = args.token

        if token.startswith("xoxp-") or token.startswith("xoxa-"):
            url = f"https://slack.com/api/auth.test?token={token}&pretty=1"
            code, body = http_post(url)

        elif token.startswith("xoxb-") or token.startswith("xoxc-"):
            url = "https://slack.com/api/auth.test"
            headers = {
                "Accept": "application/json; charset=utf-8",
                "Authorization": f"Bearer {token}",
            }
            code, body = http_post(url, headers=headers)

        else:
            return False, "Unknown Slack token format"

        if body and '"ok":true' in body.lower():
            return True, "Valid Slack Token"

        return False, f"Invalid Slack Token (status {code})"
