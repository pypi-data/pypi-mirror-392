from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get
import base64


class TwilioChecker(Provider):
    name = "twilio"
    description = "Validate Twilio Account SID + Auth Token"
    args = [
        ("-sid", "--sid", "Twilio Account SID"),
        ("-t", "--token", "Twilio Auth Token"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        sid = args.sid
        token = args.token

        url = "https://api.twilio.com/2010-04-01/Accounts.json"

        auth_str = f"{sid}:{token}".encode()
        auth_header = {"Authorization": "Basic " + base64.b64encode(auth_str).decode()}

        code, body = http_get(url, headers=auth_header)

        if code is None:
            return False, f"Request error: {body}"

        if code == 200 and '"accounts"' in body.lower():
            return True, "Valid Twilio Credentials"

        if code == 401:
            return False, "Invalid Twilio Credentials"

        return False, f"Unknown response (status {code})"
