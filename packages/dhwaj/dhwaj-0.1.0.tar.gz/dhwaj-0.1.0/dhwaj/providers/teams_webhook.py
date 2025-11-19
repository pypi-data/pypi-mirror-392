from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post


class TeamsWebhookChecker(Provider):
    name = "teams-webhook"
    description = "Validate Microsoft Teams webhook URL"
    args = [("-u", "--url", "Teams webhook URL")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        code, body = http_post(
            args.url, headers={"Content-Type": "application/json"}, json={"text": ""}
        )
        if body and "Summary or Text is required" in body:
            return True, "Valid Microsoft Teams Webhook"
        if code == 200:
            return True, "200 OK (may be valid)"
        return False, f"Invalid Teams webhook (status {code})"
