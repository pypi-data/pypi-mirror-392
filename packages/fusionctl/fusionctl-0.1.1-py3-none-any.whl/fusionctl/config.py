import json
import os
import platform
from pathlib import Path
from typing import Dict, Any, List

DEFAULT_CONFIG: Dict[str, Any] = {
    "vm_locations": [
        "~/Virtual Machines/",
        "~/Virtual Machines.localized/",
        "~/Documents/Virtual Machines/",
        "/Users/Shared/Virtual Machines/",
    ]
}


def _get_config_dir() -> Path:
    system = platform.system()

    if system == "Darwin":  # macOS
        base = Path.home() / "Library" / "Application Support" / "fusionctl"
    elif system == "Windows":
        appdata = os.getenv("APPDATA", str(Path.home()))
        base = Path(appdata) / "fusionctl"
    else:  # Linux / other Unix
        xdg = os.getenv("XDG_CONFIG_HOME")
        if xdg:
            base = Path(xdg) / "fusionctl"
        else:
            base = Path.home() / ".config" / "fusionctl"

    base.mkdir(parents=True, exist_ok=True)
    return base


CONFIG_PATH = _get_config_dir() / "config.json"

LEGACY_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


def _migrate_legacy_config() -> Dict[str, Any] | None:
    if CONFIG_PATH.exists():
        return None
    if not LEGACY_CONFIG_PATH.exists():
        return None

    try:
        with LEGACY_CONFIG_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None

    try:
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return data
    except Exception:
        return None


def load_config() -> Dict[str, Any]:
    migrated = _migrate_legacy_config()
    if migrated is not None:
        for key, value in DEFAULT_CONFIG.items():
            migrated.setdefault(key, value)
        return migrated

    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    for key, value in DEFAULT_CONFIG.items():
        data.setdefault(key, value)

    return data


def save_config(config: Dict[str, Any]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def get_vm_locations() -> List[str]:
    cfg = load_config()
    return cfg.get("vm_locations", [])


def add_vm_location(path: str) -> None:
    cfg = load_config()
    locations = cfg.get("vm_locations", [])
    if path not in locations:
        locations.append(path)
        cfg["vm_locations"] = locations
        save_config(cfg)


def remove_vm_location(path: str) -> None:
    cfg = load_config()
    locations = cfg.get("vm_locations", [])
    locations = [p for p in locations if p != path]
    cfg["vm_locations"] = locations
    save_config(cfg)