import json
import sys
from datetime import datetime
from typing import Dict, Any


def log_performance(data: Dict[str, Any]) -> None:
    """
    Log performance data as structured JSON.

    Args:
        data: Performance metrics dictionary
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": "PERF",
        **data
    }

    print(json.dumps(log_entry), file=sys.stderr, flush=True)
