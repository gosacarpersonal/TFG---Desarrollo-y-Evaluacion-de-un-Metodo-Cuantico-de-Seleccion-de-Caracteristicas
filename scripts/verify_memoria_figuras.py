#!/usr/bin/env python3
"""Static checks for the LaTeX memory figures and references.

This verifier intentionally avoids regenerating artifacts. It checks the
compiled-memory surface that matters before delivery: references, labels,
graphics files, captions and a small set of visual hygiene warnings.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TFG = ROOT / "Plantilla_Latex_GCD" / "tfgs"
TEX_MAIN = TFG / "ejemplo-memoria.tex"
TEX_DIR = TFG / "tex"
FIGS_DIR = TFG / "figs"


def strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        escaped = False
        cut = len(line)
        for idx, char in enumerate(line):
            if char == "\\":
                escaped = not escaped
                continue
            if char == "%" and not escaped:
                cut = idx
                break
            escaped = False
        lines.append(line[:cut])
    return "\n".join(lines)


def read_tex_files() -> dict[str, str]:
    files = [TEX_MAIN, TFG / "tfg.cls", *sorted(TEX_DIR.glob("*.tex"))]
    return {str(path.relative_to(ROOT)): strip_comments(path.read_text()) for path in files}


def extract_braced(text: str, command: str) -> list[str]:
    values: list[str] = []
    needle = "\\" + command
    pos = 0
    while True:
        start = text.find(needle, pos)
        if start == -1:
            break
        brace = text.find("{", start + len(needle))
        if brace == -1:
            break
        depth = 0
        for idx in range(brace, len(text)):
            char = text[idx]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    values.append(text[brace + 1 : idx])
                    pos = idx + 1
                    break
        else:
            pos = brace + 1
    return values


def find_graphics(text: str) -> list[str]:
    pattern = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
    return pattern.findall(text)


def graphic_exists(name: str) -> bool:
    path = Path(name)
    candidates = []
    if path.is_absolute():
        candidates.append(path)
    else:
        candidates.extend([TFG / path, FIGS_DIR / path])
        if not path.suffix:
            for suffix in (".png", ".pdf", ".jpg", ".jpeg"):
                candidates.extend([TFG / f"{name}{suffix}", FIGS_DIR / f"{name}{suffix}"])
    return any(candidate.exists() for candidate in candidates)


def figure_blocks(tex_by_file: dict[str, str]) -> list[dict[str, object]]:
    blocks: list[dict[str, object]] = []
    pattern = re.compile(r"\\begin\{figure\}(\[[^\]]*\])?(.*?)\\end\{figure\}", re.S)
    for filename, text in tex_by_file.items():
        for match in pattern.finditer(text):
            block = match.group(0)
            graphics = find_graphics(block)
            captions = extract_braced(block, "caption")
            labels = extract_braced(block, "label")
            line = text[: match.start()].count("\n") + 1
            blocks.append(
                {
                    "file": filename,
                    "line": line,
                    "graphics": graphics,
                    "caption": captions[0].strip() if captions else "",
                    "label": labels[0].strip() if labels else "",
                }
            )
    return blocks


def main() -> int:
    tex_by_file = read_tex_files()
    all_text = "\n".join(tex_by_file.values())

    labels = set(extract_braced(all_text, "label"))
    refs = []
    for command in ("ref", "eqref", "pageref", "autoref"):
        refs.extend(extract_braced(all_text, command))

    graphics = []
    for filename, text in tex_by_file.items():
        for graphic in find_graphics(text):
            graphics.append({"file": filename, "graphic": graphic})

    blocks = figure_blocks(tex_by_file)
    graphics_seen: dict[str, list[str]] = {}
    for block in blocks:
        for graphic in block["graphics"]:
            graphics_seen.setdefault(str(graphic), []).append(f"{block['file']}:{block['line']}")

    missing_refs = sorted(set(refs) - labels)
    missing_graphics = [
        item for item in graphics if not graphic_exists(str(item["graphic"]))
    ]
    figures_without_caption = [
        {"file": block["file"], "line": block["line"], "graphics": block["graphics"]}
        for block in blocks
        if not block["caption"]
    ]
    figures_without_label = [
        {"file": block["file"], "line": block["line"], "graphics": block["graphics"]}
        for block in blocks
        if not block["label"]
    ]
    short_captions = [
        {
            "file": block["file"],
            "line": block["line"],
            "label": block["label"],
            "words": len(re.findall(r"\w+", str(block["caption"]))),
        }
        for block in blocks
        if block["caption"] and len(re.findall(r"\w+", str(block["caption"]))) < 10
    ]
    duplicated_graphics = {
        graphic: locations
        for graphic, locations in sorted(graphics_seen.items())
        if len(locations) > 1
    }

    checks = {
        "tex_main_exists": TEX_MAIN.exists(),
        "figs_dir_exists": FIGS_DIR.exists(),
        "no_missing_refs": not missing_refs,
        "all_graphics_exist": not missing_graphics,
        "figures_have_captions": not figures_without_caption,
        "figures_have_labels": not figures_without_label,
    }

    report = {
        "counts": {
            "tex_files": len(tex_by_file),
            "labels": len(labels),
            "refs": len(refs),
            "graphics": len(graphics),
            "figure_blocks": len(blocks),
        },
        "checks": checks,
        "errors": {
            "missing_refs": missing_refs,
            "missing_graphics": missing_graphics,
            "figures_without_caption": figures_without_caption,
            "figures_without_label": figures_without_label,
        },
        "warnings": {
            "short_captions": short_captions,
            "duplicated_graphics": duplicated_graphics,
        },
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))
    ok = all(checks.values())
    print("OVERALL:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
