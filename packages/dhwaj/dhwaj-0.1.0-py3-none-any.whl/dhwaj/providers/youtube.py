from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class YouTubeChecker(Provider):
    name = "youtube"
    description = "Validate YouTube API Key"
    args = [("-k", "--key", "YouTube API Key")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = f"https://www.googleapis.com/youtube/v3/activities?part=contentDetails&maxResults=1&channelId=UC-lHJZR3Gqxm24_Vd_AJ5Yw&key={args.key}"
        code, _ = http_get(url)
        if code == 200:
            return True, "Valid YouTube API key"
        return False, f"Invalid YouTube key (status {code})"
