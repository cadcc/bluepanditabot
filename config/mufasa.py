"""
MUFASA (DCC API) settings.

Read from environment variables, falling back to a `.env` file at the repo
root (KEY=value lines, see `.env.example`). Real environment variables take
precedence over the file.
"""

import os
from pathlib import Path
from typing import Dict, Optional

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def _load_env_file(path: Path) -> Dict[str, str]:
    """Parse a simple .env file: KEY=value, optional `export`, quotes, # comments."""
    env: Dict[str, str] = {}
    if not path.is_file():
        return env
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        env[key] = value
    return env


_env = {**_load_env_file(ENV_FILE), **os.environ}

base_url: Optional[str] = _env.get("MUFASA_BASE_URL") or None
token: Optional[str] = _env.get("MUFASA_TOKEN") or None
