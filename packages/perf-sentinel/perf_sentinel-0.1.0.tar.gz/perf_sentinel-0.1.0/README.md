# PerfSentinel

Python 应用程序的长期性能测试和监控系统。

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 特性

- **简单集成** - 基于装饰器的性能监控，使用简单
- **异步支持** - 完整支持 async/await 函数，并能检测阻塞操作
- **性能分析集成** - 内置 py-spy 和 aioflame 支持
- **多种报告格式** - 生成 HTML、JSON 和 Markdown 格式的报告
- **CI/CD 就绪** - 无缝集成 GitHub Actions 和 GitLab CI
- **趋势分析** - 跟踪性能变化趋势，检测性能回归
- **自动化测试** - 使用 cron 或内置调度器定期执行性能审计

## 安装

```bash
pip install perf-sentinel
```

### 可选依赖

```bash
# 安装性能分析工具
pip install perf-sentinel[profiling]

# 安装开发工具
pip install perf-sentinel[dev]

# 安装所有可选依赖
pip install perf-sentinel[all]
```

## 快速开始

### 同步函数性能监控

```python
from perf_sentinel import perf_timing
import time

@perf_timing
def calculate_sum(n: int) -> int:
    """计算数字之和"""
    time.sleep(0.1)
    return sum(range(n))

@perf_timing(threshold_ms=100)
def slow_operation():
    """设置性能阈值的操作"""
    time.sleep(0.2)
    return "done"

# 执行函数
result = calculate_sum(1000)
slow_operation()
```

### 异步函数性能监控

```python
import asyncio
from perf_sentinel import perf_timing

@perf_timing
async def fetch_data(url: str):
    """模拟异步数据获取"""
    await asyncio.sleep(0.1)
    return {"url": url, "data": "..."}

@perf_timing
async def process_batch(items: list):
    """并发处理多个项目"""
    tasks = [fetch_data(item) for item in items]
    return await asyncio.gather(*tasks)

# 运行异步函数
asyncio.run(process_batch(["url1", "url2", "url3"]))
```

### 生成器支持

```python
@perf_timing
def data_generator(count: int):
    """同步生成器"""
    for i in range(count):
        yield i * i

@perf_timing
async def async_data_stream(count: int):
    """异步生成器"""
    for i in range(count):
        await asyncio.sleep(0.01)
        yield i
```

## 性能报告

### 使用命令行工具

```bash
# 运行性能测试并生成报告
perf-sentinel run examples/sample_sync_test.py --report-formats html json markdown

# 启用性能分析
perf-sentinel run examples/sample_async_test.py --profile --profile-format speedscope
```

### 编程方式生成报告

```python
from perf_sentinel import PerformanceReport

report = PerformanceReport(output_dir="./perf_reports")

# 添加性能指标
report.add_metric({
    "operation": "test_function",
    "type": "sync_function",
    "elapsed_ms": 123.45,
    "threshold_exceeded": False
})

# 生成多种格式的报告
report.generate_html("report.html")
report.generate_json("report.json")
report.generate_markdown("report.md")
```

## 性能分析工具

### py-spy CPU 分析

```python
from perf_sentinel import PySpyProfiler

profiler = PySpyProfiler(output_dir="./profiles")

# 分析 Python 脚本
profile_file = profiler.profile_script(
    script_path="my_test.py",
    duration=30,
    format="speedscope"
)

# 分析正在运行的进程
profile_file = profiler.profile_pid(
    pid=12345,
    duration=30,
    format="flamegraph"
)
```

### aioflame 异步性能分析

```python
from perf_sentinel import AioFlameProfiler
import asyncio

profiler = AioFlameProfiler(output_dir="./profiles")

# 分析异步函数
async def my_async_work():
    await asyncio.sleep(1)
    return "done"

result = await profiler.profile_async(my_async_work)

# 使用上下文管理器
async with profiler.profile_async_context("my_profile.svg"):
    await my_async_work()
```

## CI/CD 集成

### GitHub Actions

生成 GitHub Actions 工作流配置：

```bash
perf-sentinel init --ci github
```

这将创建 `.github/workflows/performance.yml`：

```yaml
name: Performance Testing

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 0 * * 0'

jobs:
  performance-test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install perf-sentinel[profiling]
        pip install -r requirements.txt
    - name: Run performance tests
      run: |
        perf-sentinel run tests/perf_test.py --report-formats html json
    - name: Upload reports
      uses: actions/upload-artifact@v3
      with:
        name: performance-reports
        path: perf_reports/
```

### GitLab CI

生成 GitLab CI 配置：

```bash
perf-sentinel init --ci gitlab
```

这将创建 `.gitlab-ci.yml`：

```yaml
stages:
  - performance

performance-test:
  stage: performance
  image: python:3.11
  script:
    - pip install perf-sentinel[profiling]
    - perf-sentinel run tests/perf_test.py --report-formats html json
  artifacts:
    when: always
    paths:
      - perf_reports/
    expire_in: 30 days
```

## 性能趋势分析

### 收集基准数据

```bash
# 运行性能测试并保存结果
perf-sentinel run tests/perf_test.py --report-formats json

# 结果保存在 perf_reports/perf_report.json
```

### 检测性能回归

```bash
# 分析历史数据，检测性能回归
perf-sentinel audit --threshold 10

# 输出示例：
# Found 2 performance regressions:
#   - process_data: 15.3% slower
#   - fetch_users: 23.7% slower
```

### 趋势分析

```python
from perf_sentinel import TrendAnalyzer

analyzer = TrendAnalyzer(data_dir="./perf_reports")

# 加载过去 30 天的历史数据
historical_data = analyzer.load_historical_data(days=30)

# 计算基准性能
baseline = analyzer.calculate_baseline("my_operation")
print(f"基准值: {baseline}ms")

# 检测性能回归
regressions = analyzer.detect_regressions(threshold_percent=10.0)
for reg in regressions:
    print(f"{reg['operation']}: 慢了 {reg['change_percent']}%")

# 生成趋势报告
report = analyzer.generate_trend_report(days=30)
```

## 自动化调度

### 内置调度器

```python
from perf_sentinel import PerformanceScheduler

scheduler = PerformanceScheduler()

# 每天凌晨 2:00 运行
scheduler.add_daily_audit(
    test_script="tests/perf_test.py",
    time_str="02:00"
)

# 每周一早上 8:00 运行
scheduler.add_weekly_audit(
    test_script="tests/perf_test.py",
    day="monday",
    time_str="08:00"
)

# 每 60 分钟运行一次
scheduler.add_custom_interval(
    test_script="tests/perf_test.py",
    interval_minutes=60
)

# 启动调度器（持续运行）
scheduler.run()
```

### 使用 Cron

```bash
# 编辑 crontab
crontab -e

# 添加条目，每天凌晨 2:00 运行
0 2 * * * cd /path/to/project && perf-sentinel run tests/perf_test.py --report-formats json
```

### 自定义回调函数

```python
def on_audit_complete(result):
    """审计完成时的回调函数"""
    print(f"审计完成: {result.stdout}")
    # 发送通知、更新仪表板等

scheduler.add_daily_audit(
    test_script="tests/perf_test.py",
    time_str="02:00",
    callback=on_audit_complete
)
```

## 性能指标格式

性能数据以 JSON 格式记录到 stderr：

```json
{
  "timestamp": "2025-01-17T10:30:00Z",
  "level": "PERF",
  "operation": "fetch_user_data",
  "type": "async_function",
  "elapsed_ms": 123.45,
  "has_sync_blocking": false,
  "threshold_exceeded": false
}
```

可以使用 `jq` 等工具解析输出：

```bash
python my_test.py 2>&1 | grep '"level":"PERF"' | jq .
```

## 项目结构

```
PerfSentinel/
├── perf_sentinel/
│   ├── decorators/         # 性能装饰器
│   │   ├── timing.py       # @perf_timing 装饰器
│   │   └── async_utils.py  # 异步阻塞检测
│   ├── reporter/           # 报告生成
│   │   ├── pyspy_integration.py
│   │   ├── aioflame_integration.py
│   │   └── report_builder.py
│   ├── ci/                 # CI/CD 集成
│   │   ├── github_actions.py
│   │   ├── gitlab_ci.py
│   │   └── cli.py
│   ├── audit/              # 趋势分析和调度
│   │   ├── scheduler.py
│   │   └── trend_analyzer.py
│   └── utils/              # 工具函数
├── tests/                  # 单元测试
├── examples/               # 示例脚本
└── pyproject.toml
```

## 高级用法

### 自定义操作名称

```python
@perf_timing(name="custom_db_query")
def query_database():
    pass
```

### 性能阈值设置

```python
@perf_timing(threshold_ms=500)
async def critical_operation():
    # 如果执行时间超过 500ms 将记录警告
    pass
```

### 检测异步函数中的阻塞操作

```python
@perf_timing
async def bad_async_function():
    await asyncio.sleep(0.1)

    # 这个阻塞操作会被检测到
    import time
    time.sleep(0.5)

    # 阻塞的 I/O 操作也会被检测到
    with open("file.txt") as f:
        data = f.read()

    return data
```

装饰器会在检测到阻塞操作时记录 `"has_sync_blocking": true`。

## 最佳实践

1. **建立基准** - 运行测试 3-5 次以建立稳定的基准指标
2. **定期监控** - 安排自动化性能检查
3. **CI 集成** - 在每个 PR 上运行性能测试，尽早发现性能回归
4. **设置阈值** - 为关键操作定义可接受的性能阈值
5. **跟踪趋势** - 监控长期性能趋势以识别性能退化

## 系统要求

- Python 3.8+
- schedule >= 1.2.0

### 可选依赖

- py-spy >= 0.3.14 (用于 CPU 性能分析)
- aioflame >= 0.1.0 (用于异步性能分析)
- pytest >= 7.0.0 (用于开发)

## 许可证

MIT License

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 链接

- 文档: https://github.com/yourusername/PerfSentinel
- 源代码: https://github.com/yourusername/PerfSentinel
- 问题追踪: https://github.com/yourusername/PerfSentinel/issues
