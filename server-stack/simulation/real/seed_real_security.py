#!/usr/bin/env python3
"""Seed vault, AI, proxy/cloud fixtures for RI-3."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    vault = ROOT / "seeds" / "real" / "vault"
    write(vault / "policies.hcl", 'path "secret/*" { capabilities = ["read"] }\n')
    write(vault / "secrets.yml", "secrets:\n  - path: secret/app/api-key\n    rotation_days: 90\n")
    write(vault / "tokens.yml", "tokens:\n  - id: svc-ai\n    policy: read-only\n")

    ai = ROOT / "seeds" / "real" / "ai"
    write(ai / "prompts.yml", "blocked_patterns:\n  - confidential\n  - architecture diagram\n")
    write(ai / "blocked_domains.yml", "domains:\n  - chatgpt.unapproved.ai\n")
    uploads = ai / "uploads"
    uploads.mkdir(parents=True, exist_ok=True)
    sample = uploads / "sample.bin"
    if not sample.exists():
        sample.write_bytes(b"SYNTHETIC_UPLOAD_CORPUS" * 1000)

    baseline = ROOT / "seeds" / "real" / "baseline"
    write(baseline / "peer_groups.yml", "groups:\n  finance: [cfo, analyst]\n  engineering: [dev1]\n")

    print(f"seed-real-security: vault + ai + baseline under {ROOT / 'seeds' / 'real'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
