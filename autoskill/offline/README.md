# AutoSkill Offline

English | [中文](README.zh-CN.md)

`autoskill.offline` provides batch/offline extraction workflows for archived data.
It currently covers the in-package pipelines below:

- `conversation`: archived OpenAI-format conversations -> skills
- `trajectory`: agent trajectories/events -> workflow skills

The document pipeline has been moved out into the standalone `AutoSkill4Doc`
package at the repository root.

## Document Pipeline Docs

The document pipeline has been split into a standalone root module:

- [AutoSkill4Doc README](/Users/jiezhou/Desktop/工作/其他/浦江/AutoSkill/AutoSkill4Doc/README.md)
- [AutoSkill4Doc README.zh-CN](/Users/jiezhou/Desktop/工作/其他/浦江/AutoSkill/AutoSkill4Doc/README.zh-CN.md)

Legacy note:
- `autoskill/offline/document/` has been removed.
- document extraction is now standalone in `AutoSkill4Doc` and is no longer routed through `autoskill.offline`.

## CLI Usage

Conversation:

```bash
python3 -m autoskill.offline.conversation.extract \
  --file ./conversation_logs/ \
  --user-id u1
```

Trajectory:

```bash
python3 -m autoskill.offline.trajectory.extract \
  --file ./runs/ \
  --user-id u1
```

Document (standalone package):

```bash
python3 -m AutoSkill4Doc llm-extract --file ./paper.md --dry-run
```

Document (installed script):

```bash
autoskill4doc llm-extract --file ./paper.md --json
```

## Package Layout

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
  document/
    windowing.py
  stages/
    extractor.py
    compiler.py
  store/
    versioning.py
    registry.py
```
