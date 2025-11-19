from colorama import Fore, Style


def success(msg: str) -> str:
    return f"{Fore.GREEN}[+] {msg}{Style.RESET_ALL}"


def fail(msg: str) -> str:
    return f"{Fore.RED}[-] {msg}{Style.RESET_ALL}"


def info(msg: str) -> str:
    return f"{Fore.CYAN}[*] {msg}{Style.RESET_ALL}"
