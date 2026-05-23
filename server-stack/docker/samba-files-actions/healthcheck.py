#!/usr/bin/env python3
import sys
from pathlib import Path

p = Path("/var/log/corp/samba/audit.log")
sys.exit(0 if p.exists() else 1)
