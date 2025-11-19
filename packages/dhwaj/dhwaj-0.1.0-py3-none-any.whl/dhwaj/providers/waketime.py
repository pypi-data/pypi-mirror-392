from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class WakaTimeChecker(Provider):
    name = "wakatime"
    description = "Validate WakaTime API key"
    args = [("-k", "--key", "WakaTime API key")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = f"https://wakatime.com/api/v1/users/current?api_key={args.key}"
        code, _ = http_get(url)
        if code == 200:
            return True, "Valid WakaTime API Key"
        return False, f"Invalid WakaTime key (status {code})"
