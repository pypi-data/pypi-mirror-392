from __future__ import annotations
from typing import Tuple
import argparse


class Provider:
    name: str
    description: str
    args: list[tuple[str, str, str]]

    def run(self, args: argparse.Namespace) -> Tuple[bool, str]:
        raise NotImplementedError
