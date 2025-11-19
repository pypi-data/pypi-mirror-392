from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class SpotifyChecker(Provider):
    name = "spotify"
    description = "Validate Spotify access token"
    args = [("-t", "--token", "Spotify OAuth token")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = "https://api.spotify.com/v1/me"
        headers = {"Authorization": f"Bearer {args.token}"}
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid Spotify token"
        return False, f"Invalid Spotify token (status {code})"
