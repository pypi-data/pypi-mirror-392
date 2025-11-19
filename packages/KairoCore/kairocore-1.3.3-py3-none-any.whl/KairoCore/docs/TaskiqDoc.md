# Taskiq 异步任务工具使用说明

本文档基于 `utils/kc_taskiq.py`，介绍如何使用 Taskiq 实现完全异步的分布式任务执行，并提供统一的任务提交函数。

---

## 功能概览

- 统一提交入口：`schedule_async(func, *args, **kwargs)`
  - 传入“可导入的异步函数 + 参数”，将任务推送到队列，由 worker 异步执行。
  - 返回 `TaskiqTask` 对象，可调用 `wait_result(timeout)` 等方法获取结果。
- 客户端封装：`TaskiqClient`
  - 管理 broker 启停、声明任务与提交任务。
- 默认实现：Redis Stream Broker + RedisAsyncResultBackend
  - 可靠投递（ack 支持）、结果写入 Redis（默认结果过期 1 小时）。

---

## 环境与依赖

1) 安装依赖

```bash
pip install -r requirements.txt
```

确保存在以下依赖：
- `taskiq`
- `taskiq-redis`

2) 环境变量（可选）

在 `.env` 中配置以下项（也可使用默认值）：

```
TASKIQ_REDIS_URL=redis://127.0.0.1:6379/0
TASKIQ_QUEUE_NAME=kc_taskiq_queue
```

说明：
- `TASKIQ_REDIS_URL`：Redis 连接地址（建议独立 DB 用于队列与结果）。
- `TASKIQ_QUEUE_NAME`：队列名称。

---

## 启动 worker

Taskiq 需要独立的 worker 进程来消费任务。项目中已经暴露了 `broker` 变量，位于 `KairoCore.utils.kc_taskiq`。

启动方式：

```bash
taskiq worker KairoCore.utils.kc_taskiq:broker --fs-discover
```

说明：
- `--fs-discover` 会自动扫描当前目录及子目录中名为 `tasks.py` 的模块并导入（可选）。
- 你也可以在命令中手动追加要导入的模块路径，如：
  `taskiq worker KairoCore.utils.kc_taskiq:broker my_project.tasks another.module.tasks`

---

## 代码中提交任务

统一入口：`schedule_async(func, *args, **kwargs)`

示例 1：提交一个可导入的异步函数

```python
# 文件 my_project/tasks.py
async def add(a: int, b: int) -> int:
    return a + b

# 任意位置提交任务
from KairoCore import schedule_async

async def main():
    task = await schedule_async(add, 1, 2)
    result = await task.wait_result(timeout=3)
    if not result.is_err:
        print("返回值:", result.return_value)
```

示例 2：已声明为 Taskiq 任务的函数（装饰器方式）

```python
from KairoCore.utils.kc_taskiq import broker

@broker.task(task_name="my.add")
async def add(a: int, b: int) -> int:
    return a + b

# 提交任务（两种方式等价）
task = await add.kiq(3, 4)
# 或
from KairoCore import schedule_async
task = await schedule_async(add, 3, 4)
```

返回值获取：

```python
res = await task.wait_result(timeout=5)
if res.is_err:
    print("任务异常:", res.error)
else:
    print("执行耗时(s):", res.execution_time)
    print("返回值:", res.return_value)
```

---

## 通用执行器 kc.exec 的设计

在 `schedule_async` 中，为了避免每个函数都必须预先声明为任务，我们采用“通用执行器”任务：

- 任务名：`kc.exec`
- 参数：`module`（函数所在模块路径）、`qualname`（限定名）、`args`、`kwargs`
- 逻辑：worker 端通过 `importlib.import_module(module)` 导入模块，再逐级解析 `qualname` 获取目标函数并执行。

约束：
- 函数必须是“可导入的顶层异步函数”，能够通过 `__module__` 与 `__qualname__` 在 worker 端解析。
- 局部定义的函数、lambda、或非异步函数不适用（将抛出类型错误）。

适用场景：
- 一次性提交某些异步函数，无需改动原有代码结构。
- 对于高频任务，建议使用 `@broker.task` 声明并赋予固定 `task_name`，利于路由与管理。

---

## 进阶与最佳实践

1) 结果过期
- 默认 `RedisAsyncResultBackend(result_ex_time=3600)`，结果保存 1 小时。
- 可根据场景调整或使用 `result_px_time` 毫秒级过期。

2) 可靠性与吞吐
- Redis Stream Broker 支持 ack，适合需要可靠投递的场景。
- 队列名称、连接池大小、labels 等均可在 broker 初始化时调整。

3) 模块组织
- 为便于 `--fs-discover`，建议将任务函数集中在 `tasks.py` 模块或统一命名的包中。
- 复杂业务建议使用装饰器方式声明任务，并为不同任务设置唯一的 `task_name`。

4) 与 FastAPI 集成（示例）

```python
from fastapi import FastAPI
from KairoCore.utils.kc_taskiq import TaskiqClient

app = FastAPI()
tc = TaskiqClient()

@app.on_event("startup")
async def on_startup():
    await tc.startup()

@app.on_event("shutdown")
async def on_shutdown():
    await tc.shutdown()
```

---

## 常见问题（FAQ）

1) 提交任务后没有执行
- 检查是否已启动 worker（`taskiq worker KairoCore.utils.kc_taskiq:broker`）。
- 检查 Redis 连接是否可达、权限配置是否正确。

2) 等待结果时报错或超时
- 确认任务函数是异步函数（`async def`），且 worker 能正确导入该函数。
- 如为高耗时任务，请适当增大 `wait_result(timeout)`。

3) 在非 async 环境提交任务
- 使用 `schedule_async_sync(func, *args, **kwargs)`，内部会自动创建事件循环提交（适用于脚本或测试）。

---

## 参考

- `utils/kc_taskiq.py`
- Taskiq 文档：https://taskiq-python.github.io/
- taskiq-redis：https://github.com/taskiq-python/taskiq-redis