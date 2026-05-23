#!/usr/bin/env python3
import sys
from pathlib import Path
sys.exit(0 if Path("/var/log/corp/badge/badge.jsonl").exists() else 1)
