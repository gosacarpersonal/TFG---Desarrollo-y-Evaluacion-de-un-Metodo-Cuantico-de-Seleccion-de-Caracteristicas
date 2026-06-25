from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "large_files_parts" / "manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reconstruct_file(entry: dict) -> None:
    target = ROOT / entry["original_path"]
    target.parent.mkdir(parents=True, exist_ok=True)

    with target.open("wb") as output:
        for part in entry["parts"]:
            part_path = ROOT / part
            if not part_path.exists():
                raise FileNotFoundError(f"Missing split part: {part}")
            with part_path.open("rb") as input_file:
                for chunk in iter(lambda: input_file.read(1024 * 1024), b""):
                    output.write(chunk)

    actual_size = target.stat().st_size
    if actual_size != entry["size_bytes"]:
        raise ValueError(
            f"Size mismatch for {entry['original_path']}: "
            f"{actual_size} != {entry['size_bytes']}"
        )

    actual_hash = sha256(target)
    if actual_hash != entry["sha256"]:
        raise ValueError(
            f"SHA-256 mismatch for {entry['original_path']}: "
            f"{actual_hash} != {entry['sha256']}"
        )

    print(f"OK {entry['original_path']}")


def main() -> None:
    if not MANIFEST.exists():
        print("No split-file manifest found; nothing to reconstruct.")
        return

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        reconstruct_file(entry)


if __name__ == "__main__":
    main()
