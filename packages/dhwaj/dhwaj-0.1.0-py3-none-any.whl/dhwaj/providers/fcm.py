from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post


class FirebaseFCMChecker(Provider):
    name = "firebase-fcm"
    description = "Validate Firebase Cloud Messaging (FCM) server key"
    args = [("-k", "--key", "Firebase FCM Server Key")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        key = args.key

        url = "https://fcm.googleapis.com/fcm/send"

        headers = {"Authorization": f"key={key}", "Content-Type": "application/json"}

        payload = {"registration_ids": ["1"]}

        code, body = http_post(url, headers=headers, json=payload)

        if code is None:
            return False, f"Request error: {body}"

        # Valid keys return 200 with message_id or failure array
        # Invalid keys return 401 or {"error":"InvalidRegistration"}
        if code == 200 and (
            "message_id" in body or "failure" in body or "success" in body
        ):
            return True, "Valid FCM Server Key"

        if (
            code == 401
            or "InvalidRegistration" in body
            or "Authentication Error" in body
        ):
            return False, "Invalid FCM Server Key"

        return False, f"Unknown response (status {code})"
