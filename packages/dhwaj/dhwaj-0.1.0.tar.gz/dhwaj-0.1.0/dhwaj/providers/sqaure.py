from __future__ import annotations
from typing import Tuple, Dict, Any
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post, http_get


class SquareChecker(Provider):
    name = "square"
    description = "Validate Square App ID, Client Secret, or Auth Token"
    args = [
        ("-id", "--app-id", "Square App ID"),
        ("-s", "--client-secret", "Square client secret"),
        ("-k", "--auth-token", "Square auth token"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        if args.app_id and args.client_secret:
            url = "https://squareup.com/oauth2/revoke"
            headers: Dict[str, str] = {"Content-Type": "application/json"}
            payload: Dict[str, Any] = {
                "access_token": "random",
                "client_id": args.app_id,
            }

            headers["Authorization"] = f"Client {args.client_secret}"
            code, body = http_post(url, headers=headers, json=payload)
            if code is None:
                return False, body

            if code == 200 and (not body or body.strip() == ""):
                return True, "Valid Square App ID + Client Secret (revoke accepted)"

            if (
                '"Not Authorized"' in body
                or '"service.not_authorized"' in body
                or code == 401
            ):
                return False, f"Invalid Square credentials (status {code})"

        if args.auth_token:
            url = "https://connect.squareup.com/v2/locations"
            headers = {"Authorization": f"Bearer {args.auth_token}"}
            code, body = http_get(url, headers=headers)
            if code == 200 and '"locations"' in body:
                return True, "Valid Square Auth Token"
            if code == 401:
                return False, "Invalid Square Auth Token"
            return False, f"Unknown response (status {code})"

        return False, "Provide either app-id+client-secret or auth-token"
