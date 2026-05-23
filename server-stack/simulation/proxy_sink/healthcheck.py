#!/usr/bin/env python3
import sys
from pathlib import Path
sys.exit(0 if Path("/var/log/corp/proxy/proxy_sink.jsonl").exists() else 1)
