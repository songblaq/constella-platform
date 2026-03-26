from __future__ import annotations


def build_release_prep() -> dict:
    return {
        "package_name": "constella-platform",
        "artifacts": {
            "install_bundle": "~/.constellar/manifests/install-bundle.json",
            "package_note": "~/.agenthive/projects/constella-distribution/docs/packaging-note.md",
            "public_repo": "https://github.com/songblaq/constella-platform",
        },
        "summary": {
            "visibility": "public",
            "default_branch": "main",
        },
    }
