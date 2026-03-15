# AutoSkill Offline

[English](README.md) | 中文

`autoskill.offline` 是离线批处理入口层，负责把历史数据接入技能抽取流程。
当前仍在包内维护的 pipeline 包括：

- `conversation`：历史 OpenAI 格式对话 -> skills
- `trajectory`：agent 执行轨迹/事件 -> workflow skills

文档 pipeline 已迁移为仓库根目录下的独立 `AutoSkill4Doc` 包。

## Document Pipeline 文档

文档 pipeline 已拆分为根目录独立模块：

- [AutoSkill4Doc README](/Users/jiezhou/Desktop/工作/其他/浦江/AutoSkill/AutoSkill4Doc/README.md)
- [AutoSkill4Doc README.zh-CN](/Users/jiezhou/Desktop/工作/其他/浦江/AutoSkill/AutoSkill4Doc/README.zh-CN.md)

迁移说明：

- 旧目录 `autoskill/offline/document/` 已移除。
- 文档抽取现在由 `AutoSkill4Doc` 独立承担，不再通过 `autoskill.offline` 路由。

## CLI 用法

Conversation：

```bash
python3 -m autoskill.offline.conversation.extract \
  --file ./conversation_logs/ \
  --user-id u1
```

Trajectory：

```bash
python3 -m autoskill.offline.trajectory.extract \
  --file ./runs/ \
  --user-id u1
```

Document（独立包）：

```bash
python3 -m AutoSkill4Doc llm-extract \
  --file ./paper.md \
  --domain psychology \
  --domain-type psychology \
  --family-name "认知行为疗法" \
  --dry-run
```

Document（安装脚本）：

```bash
autoskill4doc llm-extract --file ./paper.md --family-name "认知行为疗法" --json
```

## 包结构

```text
autoskill/offline/
  __init__.py
  provider_config.py
  conversation/
  trajectory/

AutoSkill4Doc/
  __init__.py
  __main__.py
  extract.py
  pipeline.py
  models.py
  prompts.py
  core/
    config.py
    provider_config.py
    common.py
  document/
    file_loader.py
    windowing.py
  stages/
    diag.py
    extractor.py
    compiler.py
    hierarchy.py
    merge.py
    migrate.py
  store/
    layout.py
    staging.py
    versioning.py
    registry.py
    visible_tree.py
```
