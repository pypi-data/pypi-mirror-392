from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post


class SlackWebhookChecker(Provider):
    name = "slack-webhook"
    description = "Validate Slack webhook URL"
    args = [("-u", "--url", "Slack webhook URL")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = args.url
        headers = {"Content-Type": "application/json"}

        code, body = http_post(url, headers=headers, json={"text": ""})

        if "missing_text_or_fallback_or_attachments" in str(body):
            return True, "Valid Slack Webhook"

        return False, f"Invalid Slack Webhook (status {code})"
