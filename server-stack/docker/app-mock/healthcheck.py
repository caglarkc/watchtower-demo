#!/usr/bin/env python3
import os
import sys
from pathlib import Path

role = os.environ.get("ROLE", "internal-app")
paths = {
    "internal-app": "/var/log/corp/app/audit.jsonl",
    "artifact": "/var/log/corp/artifact/audit.jsonl",
    "siem": "/var/log/corp/siem/audit.jsonl",
    "hypervisor": "/var/log/corp/hypervisor/audit.jsonl",
}
sys.exit(0 if Path(paths.get(role, paths["internal-app"])).exists() else 1)
