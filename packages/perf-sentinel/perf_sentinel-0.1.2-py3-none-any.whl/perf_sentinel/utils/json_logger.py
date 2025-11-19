import json
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, Any


def log_performance(data: Dict[str, Any]) -> None:
    """
    Log performance data as structured JSON.

    Args:
        data: Performance metrics dictionary
    """
    # 使用中国时区 (UTC+8)
    china_tz = timezone(timedelta(hours=8))
    china_time = datetime.now(china_tz)

    # 格式化 elapsed_ms，添加单位说明
    elapsed_ms = data.get('elapsed_ms')
    if elapsed_ms is not None:
        if elapsed_ms >= 1000:
            # 如果超过 1000ms，显示为秒
            data['elapsed_time'] = f"{elapsed_ms / 1000:.2f}s"
        else:
            data['elapsed_time'] = f"{elapsed_ms:.2f}ms"
        data['elapsed_ms'] = round(elapsed_ms, 2)  # 保留原始毫秒数

    log_entry = {
        "timestamp": china_time.strftime("%Y-%m-%d %H:%M:%S"),
        "level": "PERF",
        **data
    }

    print(json.dumps(log_entry, ensure_ascii=False), file=sys.stderr, flush=True)
