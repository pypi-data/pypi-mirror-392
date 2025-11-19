from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class ContentfulChecker(Provider):
    name = "contentful"
    description = "Validate Contentful space ID + access token"
    args = [
        ("-s", "--space", "Contentful Space ID"),
        ("-k", "--key", "Contentful Access Token"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        if not args.space or not args.key:
            return False, "space and key required"
        url = f"https://cdn.contentful.com/spaces/{args.space}/entries?access_token={args.key}"
        code, _ = http_get(url)
        if code == 200:
            return True, "Valid Contentful access token"
        if code in (401, 403):
            return False, "Invalid Contentful token"
        return False, f"Unknown response (status {code})"
