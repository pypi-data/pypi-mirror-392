from __future__ import annotations
from typing import Dict
import pkgutil
import importlib
import os

from dhwaj.providers.base import Provider


def load_providers() -> Dict[str, Provider]:
    providers: Dict[str, Provider] = {}

    pkg_path = os.path.join(os.path.dirname(__file__), "..", "providers")

    pkg_path = os.path.abspath(pkg_path)

    for module_info in pkgutil.iter_modules([pkg_path]):
        module_name = module_info.name

        module = importlib.import_module(f"dhwaj.providers.{module_name}")
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            if (
                isinstance(attr, type)
                and issubclass(attr, Provider)
                and attr is not Provider
            ):
                providers[attr.name] = attr()

    return providers
