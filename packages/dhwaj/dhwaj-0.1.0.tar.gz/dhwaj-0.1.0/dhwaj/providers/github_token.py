from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get
import base64


class GitHubTokenChecker(Provider):
    name = "github-token"
    description = "Validate GitHub personal access token"
    args = [("-t", "--token", "GitHub token"), ("-u", "--user", "GitHub username")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        token = args.token
        username = args.user if args.user else "user"

        auth_header = {
            "Authorization": "Basic "
            + base64.b64encode(f"{username}:{token}".encode()).decode()
        }

        code1, body1 = http_get("https://api.github.com/user", headers=auth_header)

        if code1 is None:
            return False, f"Request error: {body1}"

        # GitHub returns a JSON containing login when valid
        if '"login"' in body1:
            code_scope, body_scope = http_get(
                "https://api.github.com/rate_limit", headers=auth_header
            )

            scopes = "Unknown"
            if code_scope and "X-OAuth-Scopes" in body_scope:
                scopes = body_scope.split("X-OAuth-Scopes:")[1].split("\n")[0].strip()

            return True, f"Valid GitHub Token (Scopes: {scopes})"

        bearer_header = {"Authorization": f"token {token}"}

        code2, body2 = http_get(
            f"https://api.github.com/users/{username}/orgs", headers=bearer_header
        )

        if code2 and code2 != 401 and '"message"' not in body2.lower():
            return True, "Valid GitHub Token (Bearer)"

        return False, "Invalid GitHub Token"
