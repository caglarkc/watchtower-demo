#!/usr/bin/env python3
import os
import sys
from pathlib import Path

role = os.environ.get("ROLE", "postfix")
p = Path(f"/var/log/corp/{role}/{role}.jsonl")
sys.exit(0 if p.exists() else 1)
