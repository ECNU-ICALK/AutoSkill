# AutoSkill SDK（中文）

中文 | [English](README.md)

AutoSkill 是一个持续自进化的「Skill Layer」SDK：它可以从对话与行为/事件日志中自动生长出可复用、可执行的 **Skills**，并持续维护（去重/合并/版本化），在后续任务中检索并注入合适的 Skills 来提升下游任务表现。

目标：参考常见的「memory 插件」工作流，但把存储单元从“原始记忆”升级为“可执行、可复用的技能（Skill）”。

## 安装（本地开发）

```bash
python3 -m pip install -e .
```

## 快速开始

```python
from autoskill import AutoSkill, AutoSkillConfig

sdk = AutoSkill(
    AutoSkillConfig(
        llm={"provider": "mock"},
        embeddings={"provider": "hashing", "dims": 256},
        store={"provider": "inmemory"},  # 或 {"provider": "local", "path": "Skills"}
    )
)

sdk.ingest(
    messages=[
        {"role": "user", "content": "Before each release: run regression tests -> canary rollout -> monitor -> full rollout."},
        {"role": "assistant", "content": "Got it."},
    ],
    user_id="u1",
)

hits = sdk.search("How should I do a release?", user_id="u1", limit=5)
for h in hits:
    print(h.skill.name, h.score)
```

## Provider 配置示例

OpenAI：

```python
from autoskill import AutoSkill, AutoSkillConfig

sdk = AutoSkill(
    AutoSkillConfig(
        llm={"provider": "openai", "model": "gpt-4o-mini", "api_key": "YOUR_KEY"},
        embeddings={
            "provider": "openai",
            "model": "text-embedding-3-small",
            "api_key": "YOUR_KEY",
        },
        store={"provider": "inmemory"},
        maintenance_strategy="llm",
    )
)
```

DashScope Qwen（OpenAI 兼容模式）：

```python
from autoskill import AutoSkill, AutoSkillConfig

sdk = AutoSkill(
    AutoSkillConfig(
        llm={
            "provider": "dashscope",
            "model": "qwen-plus",
            "api_key": "YOUR_DASHSCOPE_API_KEY",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode",
        },
        embeddings={
            "provider": "dashscope",
            "model": "text-embedding-v4",
            "api_key": "YOUR_DASHSCOPE_API_KEY",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode",
            "extra_body": {"dimensions": 1024, "encoding_format": "float"},
        },
        store={"provider": "inmemory"},
        maintenance_strategy="llm",
    )
)
```

Anthropic：

```python
from autoskill import AutoSkill, AutoSkillConfig

sdk = AutoSkill(
    AutoSkillConfig(
        llm={"provider": "anthropic", "model": "claude-3-5-sonnet-latest", "api_key": "YOUR_KEY"},
        embeddings={"provider": "hashing", "dims": 256},
        store={"provider": "inmemory"},
        maintenance_strategy="llm",
    )
)
```

BigModel GLM（GLM-4.7 + embedding-3）：

```python
from autoskill import AutoSkill, AutoSkillConfig

sdk = AutoSkill(
    AutoSkillConfig(
        llm={
            "provider": "glm",
            "model": "glm-4.7",
            "api_key": "YOUR_ID.YOUR_SECRET",
            "auth_mode": "auto",  # 默认 auto；也可以强制 jwt 或 api_key
        },
        embeddings={
            "provider": "glm",
            "model": "embedding-3",
            "api_key": "YOUR_ID.YOUR_SECRET",
            "auth_mode": "auto",  # 默认 auto；也可以强制 jwt 或 api_key
        },
        store={"provider": "inmemory"},
        maintenance_strategy="llm",
    )
)
```

## SDK 能力概览

- `ingest(...)`：从 `messages`（对话）或 `events`（行为日志）中抽取/更新 Skills
- `search(query, ...)`：检索与当前任务相关的 Skills
- `get(skill_id)` / `list(user_id)` / `delete(skill_id)`
- `render_context(query, ...)`：把检索到的 Skills 渲染成可注入的上下文块

## Skill 格式（Agent Skill / anthropics/skills 风格）

在 SDK 内部，一个 Skill 会以结构化对象表示，并可导出为 **Agent Skill 目录制品（artifact）**：即一个目录，至少包含 `SKILL.md`（YAML frontmatter + Markdown 正文），参考 `anthropics/skills` 的组织方式。

核心字段：

- `name`：短、可检索的标题
- `description`：该技能的用途与适用场景
- `instructions`（即 `prompt`）：可复用、可直接执行的技能指令
- `triggers`：触发/使用条件
- `examples`：可选示例
- `tags`：主题标签
- `version`：语义化版本（默认 `0.1.0`，合并时 bump patch）

Agent Skill 制品：

- `Skill.files["SKILL.md"]`：生成的 `SKILL.md`
- `AutoSkill.export_skill_md(skill_id)`：导出 `SKILL.md` 文本
- `AutoSkill.write_skill_dir(skill_id, root_dir=...)`：写出一个技能目录（可附带脚本/资源）
- `AutoSkill.write_skill_dirs(user_id=..., root_dir=...)`：批量写出用户所有技能目录

## LLM / Embeddings / Store

AutoSkill 采用可插拔架构：

- LLM：`mock`（离线）、`openai`、`dashscope`（Qwen）、`anthropic`、`glm`（BigModel GLM-4.7）
- Embeddings：`hashing`（离线）、`openai`、`dashscope`（Qwen）、`glm`（BigModel embedding-3）
- Store：`inmemory`（离线）、`local`（按目录持久化：`Users/<user_id>/...` + 共享库 `Common/...`；向量索引持久化以加速检索）

## 架构说明

AutoSkill 主要由几层可组合模块构成（类似 Mem0 的「client + provider + store」分层），并额外提供 Skill Management 层来负责抽取与维护。

### 核心数据流

**Ingest（生长/维护 skills）：**

1) `AutoSkill.ingest(...)` 接收 `messages`（对话）或 `events`（行为日志）
2) `SkillExtractor.extract(...)` 产生最多 1 个 `SkillCandidate`（LLM 抽取或启发式）
3) `SkillMaintainer.apply(...)` 基于相似技能检索做 add/merge/discard 决策并 upsert
4) `SkillStore.upsert(...)` 把技能保存为 Agent Skill 制品（`SKILL.md` + 可选资源）

**Retrieve（使用 skills）：**

1)（可选）把用户 query 重写为更适合检索的 query（关注能力/需求/约束，而非粘贴内容细节）
2) 用配置的 embedding provider 生成 query 向量
3) `SkillStore.search(...)` 对技能向量做检索，返回 `SkillHit`
4) 通过 `render_skills_context(...)` 把选中的技能渲染为可注入上下文块

### 本地持久化目录结构（Local Store）

当 `store={"provider":"local","path":"Skills"}` 时，推荐目录结构如下：

```text
Skills/
  Users/
    <user_id>/
      <skill-slug>/
        SKILL.md
        scripts/…            (可选)
        references/…         (可选)
        assets/…             (可选)
  Common/
    <skill-slug>/SKILL.md
    <library-name>/<skill-slug>/SKILL.md
  vectors/
    <index>.meta.json
    <index>.ids.txt
    <index>.vecs.f32
```

说明：
- `Common/` 是共享技能库；`Users/<user_id>/` 是用户私有技能。
- 也支持通过 `--library-dir` 加载额外只读技能库（见 examples）。
- 向量缓存会按 embedding 签名（provider + model + 可选 dimensions）分开存储，避免切换 embedding 模型后混用旧向量。

### 交互式流程（Retrieve + Extract）

在 `autoskill.interactive` 中，每轮用户输入会先执行检索，再生成回复。抽取会经过 gating 以控制质量；在 `auto` 模式下，抽取评估只在话题边界或周期性 checkpoint 执行，并且会延迟到下一条用户消息，把它作为“反馈信号”（是否解决/是否要继续修改）再决定是否 ingest。

## 仓库结构（代码地图）

### 顶层

- `README.md`：英文文档与架构说明
- `README.zh-CN.md`：中文文档与架构说明
- `pyproject.toml`：打包与依赖
- `Skills/`：默认本地 store 根目录（运行时创建/使用）
- `autoskill/`：SDK 源码
- `examples/`：端到端示例脚本

### `autoskill/`（SDK）

- `autoskill/__init__.py`：对外导出（`AutoSkill`、`AutoSkillConfig`、核心模型）
- `autoskill/client.py`：SDK 入口（ingest/search/render/export/import）
- `autoskill/config.py`：`AutoSkillConfig`（可序列化配置 + 默认值）
- `autoskill/models.py`：核心数据结构（`Skill`、`SkillHit`、`SkillExample`、状态枚举）
- `autoskill/render.py`：把选中的 skills 渲染为可注入的 context block
- `autoskill/py.typed`：类型提示标记

#### `autoskill/llm/`（对话模型 Provider）

- `autoskill/llm/__init__.py`：LLM provider 层导出（`LLM`、`build_llm`）
- `autoskill/llm/base.py`：LLM 接口（`complete(system, user, temperature)`）
- `autoskill/llm/factory.py`：provider 工厂（`mock|openai|dashscope|glm|anthropic`）
- `autoskill/llm/mock.py`：离线 mock LLM（固定输出）
- `autoskill/llm/openai.py`：最小 OpenAI 兼容 Chat Completions 客户端（OpenAI + DashScope 共用）
- `autoskill/llm/glm.py`：BigModel GLM-4.7 客户端（`auth_mode` 支持 auto/jwt/api_key）
- `autoskill/llm/anthropic.py`：最小 Anthropic Messages 客户端

#### `autoskill/embeddings/`（Embedding Provider）

- `autoskill/embeddings/__init__.py`：Embedding provider 层导出（`EmbeddingModel`、`build_embeddings`）
- `autoskill/embeddings/base.py`：Embedding 接口（`embed(texts) -> vectors`）
- `autoskill/embeddings/factory.py`：provider 工厂（`hashing|openai|dashscope|glm`）
- `autoskill/embeddings/hashing.py`：离线 hashing embedding（无网络、快速 baseline）
- `autoskill/embeddings/openai.py`：最小 OpenAI 兼容 embeddings 客户端（OpenAI + DashScope 共用）
- `autoskill/embeddings/bigmodel.py`：BigModel embedding-3 客户端（auto/jwt/api_key）

#### `autoskill/skill_management/`（抽取 + 维护 + 格式）

- `autoskill/skill_management/__init__.py`：skill management 相关导出（extract/maintain/store/vector 等）
- `autoskill/skill_management/extraction.py`：技能抽取（LLM 抽取 + 修复 + 启发式兜底）
- `autoskill/skill_management/maintenance.py`：技能维护（去重/合并/版本；可选 LLM 决策）
- `autoskill/skill_management/importer.py`：导入外部 Agent Skills（扫描 `**/SKILL.md`）
- `autoskill/skill_management/artifacts.py`：导出/写入技能制品（`SKILL.md`、技能目录）

##### `autoskill/skill_management/formats/`

- `autoskill/skill_management/formats/__init__.py`：格式导出（render/parse helpers）
- `autoskill/skill_management/formats/agent_skill.py`：Agent Skill 目录制品格式（`SKILL.md` 渲染/解析）

##### `autoskill/skill_management/stores/`

- `autoskill/skill_management/stores/__init__.py`：store 导出（`SkillStore`、`build_store`）
- `autoskill/skill_management/stores/base.py`：`SkillStore` 接口
- `autoskill/skill_management/stores/factory.py`：store 工厂（并生成按 embedding 签名区分的向量索引名）
- `autoskill/skill_management/stores/inmemory.py`：内存 store（无持久化）
- `autoskill/skill_management/stores/local.py`：本地文件系统 store（`Users/` + `Common/`；向量缓存）

##### `autoskill/skill_management/vectors/`

- `autoskill/skill_management/vectors/__init__.py`：向量后端导出（`VectorIndex`、`FlatFileVectorIndex`）
- `autoskill/skill_management/vectors/base.py`：向量索引接口
- `autoskill/skill_management/vectors/flat.py`：依赖零的持久化平面索引（meta/ids/vecs 文件）

#### `autoskill/interactive/`（交互式编排）

- `autoskill/interactive/__init__.py`：交互模块导出（`InteractiveChatApp`、`InteractiveConfig` 等）
- `autoskill/interactive/app.py`：交互编排（rewrite → retrieve → respond → gate/extract）
- `autoskill/interactive/config.py`：交互配置（scope/阈值/窗口等）
- `autoskill/interactive/commands.py`：命令解析（`/help`、`/extract_now` 等）
- `autoskill/interactive/io.py`：IO 抽象（便于嵌入其他前端）
- `autoskill/interactive/rewriting.py`：检索 query 重写
- `autoskill/interactive/selection.py`：可选 LLM selector（决定是否注入检索到的 skills）
- `autoskill/interactive/gating.py`：抽取 gating（启发式 + LLM gate）

#### `autoskill/utils/`（通用工具）

- `autoskill/utils/__init__.py`：小型工具导出（JSON 解析、脱敏、时间戳）
- `autoskill/utils/units.py`：混合语言长度度量 + 截断（CJK 按字、英文按词）
- `autoskill/utils/json.py`：LLM 输出的容错 JSON 提取
- `autoskill/utils/text.py`：关键词提取（标签/启发式）
- `autoskill/utils/redact.py`：源数据脱敏（减少把敏感信息喂给 LLM）
- `autoskill/utils/time.py`：时间戳
- `autoskill/utils/bigmodel_auth.py`：BigModel JWT/auth 工具（GLM + embedding-3 使用）

### `examples/`（示例脚本）

- `examples/__init__.py`：示例脚本入口（`python3 -m examples.<script>`）
- `examples/basic_ingest_search.py`：最小 ingest + search 演示
- `examples/interactive_chat.py`：交互式演示（`mock|glm|dashscope|openai|anthropic`）
- `examples/personalized_email_demo.py`：迭代写作 → 抽取 → 检索的脚本化 demo
- `examples/local_persistent_store.py`：本地持久化 store demo
- `examples/bigmodel_glm_persistent_store.py`：GLM + embedding-3 + 本地持久化 demo
- `examples/bigmodel_glm_embed_extract.py`：BigModel 的 embed + extract 流程 demo
- `examples/dashscope_qwen_chat.py`：DashScope chat demo
- `examples/dashscope_qwen_embeddings.py`：DashScope embeddings demo
- `examples/import_agent_skills.py`：导入外部 Agent Skills 到本地 store
- `examples/normalize_skill_ids.py`：为 store 根目录下缺失 `id:` 的 `SKILL.md` 做规范化

