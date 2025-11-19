from __future__ import annotations
from typing import Tuple, Dict, Any
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post


class WeglotChecker(Provider):
    name = "weglot"
    description = "Validate Weglot API key"
    args = [("-k", "--key", "Weglot API key")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = "https://api.weglot.com/translate?api_key=" + args.key
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        payload: Dict[str, Any] = {
            "l_from": "en",
            "l_to": "fr",
            "request_url": "https://example.com/",
            "words": [{"w": "test", "t": 1}],
        }
        code, _ = http_post(url, headers=headers, json=payload)
        if code == 200:
            return True, "Valid Weglot API key"
        return False, f"Invalid Weglot key (status {code})"
