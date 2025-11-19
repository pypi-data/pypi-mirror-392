#!/usr/bin/env python3
from __future__ import annotations

import argparse
import signal
import sys
from typing import Dict, List, Optional, Sequence, Tuple, Protocol, NoReturn

import urllib3
from dhwaj.utils.loader import load_providers
from dhwaj.utils.colors import success, fail, info

urllib3.disable_warnings()


class Provider(Protocol):
    name: str
    description: str
    # sequence of (short_flag, long_flag, help_text)
    args: Sequence[Tuple[str, str, str]]

    # run should accept argparse.Namespace and return (ok, message)
    def run(self, args: argparse.Namespace) -> Tuple[bool, str]: ...


def stop(sig: int, frame: Optional[object]) -> NoReturn:
    print("\nInterrupted. Exiting gracefully...")
    sys.exit(0)


signal.signal(signal.SIGINT, stop)


def main() -> None:
    # loader is guaranteed to return str -> Provider based on our Protocol
    providers: Dict[str, Provider] = load_providers()

    provider_names: List[str] = list(providers.keys())

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("provider", nargs="?")
    parser.add_argument("-h", "--help", action="store_true")
    known, unknown = parser.parse_known_args()

    # No provider passed → show list
    if known.provider is None:
        print("\nAvailable providers:\n")
        for p in provider_names:
            print(f"  - {p}")
        print("\nUse:")
        print("  dhwaj <provider> -h\n")
        return

    # Invalid provider
    if known.provider not in providers:
        print("Provider not supported.\n")
        print("Available providers:")
        for p in provider_names:
            print(f"  - {p}")
        return

    provider: Provider = providers[known.provider]

    # Provider help screen
    if known.help and not unknown:
        print(f"\n{provider.name.title()}")
        print(f"Description: {provider.description}\n")

        print("Options:")
        for short, long, helptext in provider.args:
            print(f"  {short:<3} , {long:<15} {helptext}")

        print("\nUsage:")
        usage = f"dhwaj {provider.name} "
        for short, _long, _ in provider.args:
            usage += f"{short} <value> "
        print(" ", usage)
        print("")
        return

    # Build provider-specific parser
    provider_parser = argparse.ArgumentParser(
        description=f"{provider.name} checker",
        prog=f"dhwaj {provider.name}",
    )

    for short, long, _ in provider.args:
        provider_parser.add_argument(short, long)

    args = provider_parser.parse_args(unknown)

    print(info(f"Checking {provider.name}..."))

    ok, message = provider.run(args)

    print(success(message) if ok else fail(message))


if __name__ == "__main__":
    main()
