from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.services.errors import ArtifactMalformed, ArtifactNotFound


def read_json_artifact(path: Path | None, kind: str) -> Any:
    if path is None or not path.is_file():
        raise ArtifactNotFound(f"{kind} artifact has not been produced or configured.")
    try:
        with path.open(encoding="utf-8") as artifact:
            return json.load(artifact)
    except (OSError, json.JSONDecodeError) as exc:
        raise ArtifactMalformed(f"{kind} artifact is unreadable or malformed.") from exc
