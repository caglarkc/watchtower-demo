#!/usr/bin/env python3
import urllib.request
import sys
try:
    urllib.request.urlopen("http://127.0.0.1:9201/health", timeout=3)
    sys.exit(0)
except Exception:
    sys.exit(1)
