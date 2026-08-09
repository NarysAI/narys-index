from __future__ import annotations

import sys
from pathlib import Path

import yaml


PUB_URLS = {
    "https://github.com/NarysAI/PUB",
    "https://github.com/NarysAI/PUB.git",
}


def main() -> int:
    index_root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    pub_root = Path(sys.argv[2] if len(sys.argv) > 2 else "../PUB").resolve()
    covered_roots: set[str] = set()
    errors: list[str] = []

    for config_path in sorted(index_root.rglob("partcad.yaml")):
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        imports = data.get("import") or {}
        if not isinstance(imports, dict):
            continue
        for name, raw in imports.items():
            if not isinstance(raw, dict) or str(raw.get("url", "")).rstrip("/") not in PUB_URLS:
                continue
            rel_path = str(raw.get("relPath", "")).strip("/")
            if not rel_path:
                errors.append(f"{config_path.relative_to(index_root)}: PUB import {name!r} has no relPath")
                continue
            if not (pub_root / rel_path).is_dir():
                errors.append(f"{config_path.relative_to(index_root)}: missing PUB directory: {rel_path}")
            covered_roots.add(rel_path)

    packages = []
    for config_path in sorted(pub_root.rglob("partcad.yaml")):
        package_path = config_path.parent.relative_to(pub_root).as_posix()
        packages.append(package_path)
        if not any(package_path == root or package_path.startswith(root + "/") for root in covered_roots):
            errors.append(f"PUB package is absent from the website tree: {package_path}")

    if errors:
        print("\n".join(errors))
        return 1
    print(f"All {len(packages)} PUB packages are covered by {len(covered_roots)} website imports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
