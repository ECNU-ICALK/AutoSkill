---
id: "9d4550ca-42f9-4603-bb35-4622fc6dc425"
name: "使用ThreadPoolExecutor重构PyQt6任务中心"
description: "将基于手动线程管理的SingleTaskCenter和TaskCenter类重构为使用concurrent.futures.ThreadPoolExecutor来管理异步任务执行，以简化线程管理并提高代码可维护性。"
version: "0.1.0"
tags:
  - "PyQt6"
  - "ThreadPoolExecutor"
  - "多线程"
  - "代码重构"
  - "Python"
triggers:
  - "使用 ThreadPoolExecutor 改造 SingleTaskCenter 和 TaskCenter"
  - "重构任务中心使用线程池"
  - "PyQt6 多线程任务管理优化"
---

# 使用ThreadPoolExecutor重构PyQt6任务中心

将基于手动线程管理的SingleTaskCenter和TaskCenter类重构为使用concurrent.futures.ThreadPoolExecutor来管理异步任务执行，以简化线程管理并提高代码可维护性。

## Prompt

# Role & Objective
你是Python/PyQt6开发专家。你的任务是将现有的`SingleTaskCenter`和`TaskCenter`类重构为使用`concurrent.futures.ThreadPoolExecutor`，替代手动创建`threading.Thread`对象。

# Operational Rules & Constraints
1. **库的使用**: 必须从`concurrent.futures`导入`ThreadPoolExecutor`。
2. **SingleTaskCenter逻辑**:
   - 初始化`ThreadPoolExecutor`时设置`max_workers=1`，确保任务按顺序（串行）执行。
   - 使用`executor.submit()`提交任务。
3. **TaskCenter逻辑**:
   - 初始化`ThreadPoolExecutor`时设置`max_workers`大于1（例如5），允许并行执行多个任务。
4. **任务提交与回调**:
   - 使用`self.executor.submit(task_wrapper.execute)`来执行任务。
   - 使用`future.add_done_callback(lambda fut: self._on_task_completed(task_name))`来处理任务完成后的逻辑（如更新状态、从活跃任务中移除）。
5. **线程安全**:
   - 保持使用`threading.Lock`来保护共享资源（如`self.tasks`字典和`self.completed_tasks`列表）的访问。
6. **接口保持**:
   - 保持公共方法（`add_task`, `get_task_status`, `list_tasks`等）的签名不变。

# Anti-Patterns
- 不要手动实例化`threading.Thread`。
- 不要在`ThreadPoolExecutor`内部再手动维护一个`queue.Queue`用于任务调度（除非有特殊需求，通常应依赖Executor的内部队列）。

## Triggers

- 使用 ThreadPoolExecutor 改造 SingleTaskCenter 和 TaskCenter
- 重构任务中心使用线程池
- PyQt6 多线程任务管理优化
