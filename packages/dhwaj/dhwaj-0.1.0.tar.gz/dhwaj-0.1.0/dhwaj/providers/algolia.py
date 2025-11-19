from __future__ import annotations
from typing import Tuple, Dict
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class AlgoliaChecker(Provider):
    name = "algolia"
    description = "Validate Algolia Application ID + API Key + optional index name"

    args = [
        ("-k", "--key", "Algolia API key"),
        ("-a", "--appid", "Algolia Application ID"),
        ("-i", "--index", "Index name (optional)"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        if args.index:
            url = f"https://{args.appid}-1.algolianet.com/1/indexes/{args.index}"
        else:
            url = f"https://{args.appid}-1.algolianet.com/1/indexes/"
        headers: Dict[str, str] = {
            "content-type": "application/json",
            "x-algolia-api-key": args.key,
            "x-algolia-application-id": args.appid,
        }
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid Algolia API Key"
        return False, f"Invalid Algolia key (status {code})"
