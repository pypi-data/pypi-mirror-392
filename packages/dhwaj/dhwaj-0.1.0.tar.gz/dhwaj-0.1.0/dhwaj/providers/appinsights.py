from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class AppInsightsChecker(Provider):
    name = "appinsights"
    description = "Validate Azure Application Insights App ID + API Key"
    args = [
        ("-k", "--key", "Application Insights API Key"),
        ("-a", "--app-id", "Application Insights App ID"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = f"https://api.applicationinsights.io/v1/apps/{args.app_id}/metrics/requests/count"
        headers = {"x-api-key": args.key}
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid Application Insights API key"
        return False, f"Invalid App Insights key (status {code})"
