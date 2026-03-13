---
id: "c9be80ac-ea1c-4824-bccb-8e06bac220bf"
name: "os / asyncio / path"
description: "General SOP for common requests related to os, asyncio, path."
version: "0.1.0"
tags:
  - "os"
  - "asyncio"
  - "path"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# os / asyncio / path

General SOP for common requests related to os, asyncio, path.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) async def extract_zip(compress_file_path: str, extract_path: str
2) async with zipfile.ZipFile(compress_file_path, "r") as zip_ref
3) await zip_ref.extractall(extract_path)  并通过 asyncio 的 create_task 在循环中创建多个任务并加入到列表中，最后通过gather方法调用列表中的任务是否可行，和你的方法比起来哪个更好
4) asyncio.run() 作用
5) async def tar_extract(tmp_tar_dir
6) def _extract_tar(tar_file_path, logs_folder
7) with tarfile.open(tar_file_path, "r:gz") as tar_ref
8) tar_ref.extractall(logs_folder, filter="data
9) loop = asyncio.get_running_loop
10) for dirpath, _, filenames in os.walk(tmp_tar_dir

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
