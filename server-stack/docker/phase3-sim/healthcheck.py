#!/usr/bin/env python3
import os
import sys
from pathlib import Path

ROLE = os.environ.get("ROLE", "vault")
paths = {
    "vault": "/var/log/corp/vault/audit.jsonl",
    "mattermost": "/var/log/corp/mattermost/chat.jsonl",
    "cups": "/var/log/corp/cups/print.jsonl",
    "wiki": "/var/log/corp/wiki/access.jsonl",
    "suitecrm": "/var/log/corp/suitecrm/crm.jsonl",
    "dlp": "/var/log/corp/dlp/health.jsonl",
    "cloud": "/var/log/corp/cloud/upload.jsonl",
    "activity": "/var/log/corp/activity/input.jsonl",
}
sys.exit(0 if Path(paths.get(ROLE, paths["vault"])).exists() else 1)
