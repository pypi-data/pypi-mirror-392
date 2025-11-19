from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
import subprocess


class AWSChecker(Provider):
    name = "aws"
    description = "Validate AWS Access Key + Secret Key"
    args = [
        ("-ak", "--access-key", "AWS Access Key ID"),
        ("-sk", "--secret-key", "AWS Secret Access Key"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        access = args.access_key
        secret = args.secret_key
        if not access or not secret:
            return False, "access-key and secret-key required"
        env = {"AWS_ACCESS_KEY_ID": access, "AWS_SECRET_ACCESS_KEY": secret}
        try:
            p = subprocess.run(
                ["aws", "sts", "get-caller-identity"],
                capture_output=True,
                text=True,
                env={**env},
                timeout=15,
            )
            out = p.stdout + p.stderr
            if p.returncode == 0 and "UserId" in out:
                return True, "Valid AWS credentials"
            return False, f"Invalid AWS credentials: {out.strip()}"
        except Exception as e:
            return False, str(e)
