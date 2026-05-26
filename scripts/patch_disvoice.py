#!/usr/bin/env python3
"""
Patch DisVoice for SciPy compatibility (balanced version).

What it does:
1) Find current env's site-packages/disvoice
2) Replace two incompatible SciPy imports
3) Create .bak backup before first write
4) Safe to run multiple times (idempotent)
"""

from pathlib import Path
import site
import shutil
import sys


# Centralized patch rules: relative file -> (old_text, new_text) list
PATCH_RULES = {
    "glottal/peakdetect.py": [
        ("from scipy import fft, ifft", "from scipy.fft import fft, ifft"),
    ],
    "glottal/GCI.py": [
        (
            "from scipy.integrate import cumtrapz",
            "from scipy.integrate import cumulative_trapezoid as cumtrapz",
        ),
    ],
}


def find_disvoice_root() -> Path:
    """
    Locate disvoice package under current Python environment.
    Raises RuntimeError if not found.
    """
    candidates = []
    try:
        candidates.extend(site.getsitepackages())
    except Exception:
        pass
    try:
        candidates.append(site.getusersitepackages())
    except Exception:
        pass

    for sp in candidates:
        pkg = Path(sp) / "disvoice"
        if pkg.exists() and pkg.is_dir():
            return pkg

    raise RuntimeError("Cannot find disvoice package. Activate the target env first.")


def backup_once(file_path: Path) -> None:
    """
    Create one backup file: xxx.py -> xxx.py.bak (only if not exists).
    """
    bak = file_path.with_suffix(file_path.suffix + ".bak")
    if not bak.exists():
        shutil.copy2(file_path, bak)
        print(f"[backup] {bak}")


def patch_file(file_path: Path, replacements: list[tuple[str, str]]) -> bool:
    """
    Apply replacements to one file.
    Returns True if file content changed.
    """
    text = file_path.read_text(encoding="utf-8")
    original = text

    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
            print(f"[patch ] {file_path.name}: replaced '{old}'")
        elif new in text:
            print(f"[skip  ] {file_path.name}: already patched")
        else:
            print(f"[warn  ] {file_path.name}: pattern not found -> {old}")

    if text != original:
        backup_once(file_path)
        file_path.write_text(text, encoding="utf-8")
        print(f"[write ] {file_path}")
        return True

    return False


def main() -> int:
    try:
        root = find_disvoice_root()
    except RuntimeError as e:
        print(f"[error ] {e}")
        return 1

    print(f"[info  ] disvoice root: {root}")

    changed = 0
    for rel_path, replacements in PATCH_RULES.items():
        target = root / rel_path
        if not target.exists():
            print(f"[warn  ] missing file: {target}")
            continue
        if patch_file(target, replacements):
            changed += 1

    print(f"[done  ] patched files: {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())