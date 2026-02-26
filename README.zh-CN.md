# AutoSkill: 基于技能自进化的经验驱动终身学习

中文 | [English](README.md)

AutoSkill 是 **Experience-driven Lifelong Learning（ELL，经验驱动终身学习）** 的工程化实践。
它从真实交互经验（对话 + 行为/事件）中学习，自动生成可复用技能，并通过合并与版本演进持续优化已有技能。

![AutoSkill Framework](imgs/Framework.png)

## News

- **2025-03-26**: 发布 **AutoSkill-OpenClaw-Plugin 1.0**。
- **2025-02-04**：发布 **AutoSkill 1.0**。

## 1. 快速开始：Web UI

```bash
python3 -m pip install -e .
export INTERNLM_API_KEY="YOUR_INTERNLM_API_KEY"
export DASHSCOPE_API_KEY="YOUR_DASHSCOPE_API_KEY"
python3 -m examples.web_ui \
  --host 127.0.0.1 \
  --port 8000 \
  --llm-provider internlm \
  --embeddings-provider qwen \
  --store-dir SkillBank \
  --user-id u1 \
  --skill-scope all \
  --rewrite-mode always \
  --extract-mode auto \
  --extract-turn-limit 1 \
  --min-score 0.4 \
  --top-k 1
```

启动后打开 `http://127.0.0.1:8000`。

## 1.1 标准 API 代理

AutoSkill 也可以作为反向代理部署，对外暴露 OpenAI 兼容接口，并在内部自动执行：
- 每次对话请求的技能检索与注入
- 回答后的异步技能抽取与维护

```bash
python3 -m pip install -e .
export INTERNLM_API_KEY="YOUR_INTERNLM_API_KEY"
export DASHSCOPE_API_KEY="YOUR_DASHSCOPE_API_KEY"
python3 -m examples.openai_proxy \
  --host 127.0.0.1 \
  --port 9000 \
  --llm-provider internlm \
  --embeddings-provider qwen \
  --served-model intern-s1-pro \
  --served-model gpt-5.2 \
  --store-dir SkillBank \
  --skill-scope all \
  --rewrite-mode always \
  --min-score 0.4 \
  --top-k 1
```

支持接口：
- `POST /v1/chat/completions`（支持 `stream=true`）
- `POST /v1/embeddings`
- `GET /v1/models`
- `GET /health`

模型列表（`/v1/models`）配置方式：
- 使用 `--served-model <model_id>` 多次传入，或
- 使用 `--served-models-json '[{"id":"gpt-5.2"},{"id":"gemini-3-pro-preview","object":"gemini","owned_by":"openai"}]'`
- 若未配置，代理会返回当前 LLM 配置模型作为单条默认项

按请求隔离用户（部署时 `--user-id` 为可选）：
- 请求体字段 `user`（最高优先级）
- 或请求头 `X-AutoSkill-User`
- 或 `Authorization: Bearer <JWT>` 的 payload 字段 `id`
- 最后回退到代理默认用户（配置的 `--user-id`，或默认 `u1`）

流式聊天调用示例（`stream=true`）：

```bash
curl -N http://127.0.0.1:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "intern-s1-pro",
    "stream": true,
    "messages": [
      {"role": "user", "content": "请简要总结技能自进化的核心思路。"}
    ]
  }'
```

如果启用了代理鉴权（`--proxy-api-key`），请额外添加：

```bash
-H "Authorization: Bearer $AUTOSKILL_PROXY_API_KEY"
```

## 1.2 一键部署（Docker Compose）

```bash
cp .env.example .env
# 编辑 .env，填写 API Key（至少一个对话模型和一个 embedding 模型）
docker compose up --build -d
```

启动后访问：
- Web UI：`http://127.0.0.1:8000`
- API Proxy：`http://127.0.0.1:9000`

停止服务：

```bash
docker compose down
```

Compose 会同时拉起两个服务：
- `autoskill-web`（`examples.web_ui`）
- `autoskill-proxy`（`examples.openai_proxy`）

两个服务共享同一份持久化存储：
- 宿主机：`./SkillBank`
- 容器内：`/data/SkillBank`

## 1.3 技能生命周期示例（三个方面）

### A) 自动判断 + 反馈触发抽取与技能管理（v0.1.0）

如果用户只是提出“写一份报告”这类通用一次性请求，且没有给出稳定偏好或纠偏反馈，
AutoSkill 会默认不新增技能（抽取结果为空），避免产生噪声技能。

当用户给出可复用的稳定约束（例如“不要幻觉”）时，AutoSkill 会触发抽取或与已有技能合并，形成 `v0.1.0`。
技能管理以后端自动为主（自动新增/合并），并支持人工编辑保存或删除 `SKILL.md`。

![技能抽取（日常场景）](imgs/skill_extraction.png)
*图注：日常场景中，可复用的写作约束被抽取为新技能（`v0.1.0`）。*

![技能抽取（科研场景）](imgs/science_skill_extraction.png)
*图注：科研场景中，可复用的实验/流程约束（如硬性阈值、必选 SOP 步骤）被抽取为技能（`v0.1.0`）。*

### B) 技能更新（v0.1.1）

后续交互中当用户继续给出新增约束或偏好变化时，AutoSkill 会优先更新已有技能而不是产生重复技能，
将版本从 `v0.1.0` 演进到 `v0.1.1`。

![技能更新（日常场景）](imgs/skill_update.png)
*图注：日常场景中，后续用户反馈持续补充约束，技能演进到 `v0.1.1`。*

![技能更新（科研场景）](imgs/science_skill_update.png)
*图注：科研场景中，新增技术反馈会更新既有技能而非新增重复技能（`v0.1.1`）。*

### C) 技能使用

当再次出现类似任务（例如撰写一份**自进化智能体的政府报告**）时，系统会检索并使用该技能，
输出更贴合用户需求的结果。

![技能使用（日常场景）](imgs/skill_utilize.png)
*图注：日常场景中，演进后的技能会在后续相似任务中被检索并复用。*

![技能使用（科研场景）](imgs/science_skill_utilize.png)
*图注：科研场景中，演进后的科研技能会在后续同类任务中被检索并复用。*

## 2. 项目核心特点

- **经验驱动技能持续进化**：直接从真实用户交互和行为轨迹中抽取可复用能力，并持续进行版本演进与维护，让系统越用越贴合用户需求。
- **通用技能格式**：采用 Agent Skill 形态（`SKILL.md`），具备可解释、可编辑的优势：结构清晰、内容可审阅、可按需人工修改；既可导入已有技能，也可将抽取技能迁移到其他系统。
- **标准接口服务化**：以可插拔方式接入现有大模型；通过 OpenAI 兼容代理，可在不改业务调用形态的情况下接入 AutoSkill。

## 2.1 解耦连接器与向量后端

- **LLM 连接器注册机制**：`build_llm(...)` 支持运行时注册（`register_llm_connector`）和配置化自定义构建器（`connector_factory="module:function"`），新增模型后端无需修改 SDK 内核代码。
- **Embedding 连接器注册机制**：`build_embeddings(...)` 提供同样的插件化方式（`register_embedding_connector` / `connector_factory`），更接近 LangChain/LiteLLM 的接入体验。
- **向量后端抽象**：本地技能库通过 `build_vector_index(...)` 接入可插拔向量后端；默认 `flat`，并支持可选 `chroma`、`milvus`、`pinecone`（按依赖启用）。

`store` 配置示例：

```python
store = {
  "provider": "local",
  "path": "SkillBank",
  "vector_backend": "flat",  # flat | chroma | milvus | pinecone | custom
  "vector_backend_config": {
    # 自定义插件后端示例：
    # "backend_factory": "your_pkg.your_module:build_vector_backend"
  },
}
```

## 3. 系统工作流

### 3.1 学习与进化流程

```text
经验数据（messages/events）
  -> 技能抽取（candidate）
  -> 技能维护（add / merge / discard）
  -> 技能存储（Agent Skill + 向量索引）
```

- 每次尝试最多产出一个高质量候选技能。
- 维护阶段先做相似匹配，再决定新增/合并/丢弃。
- 合并后自动递增 patch 版本，形成长期演化轨迹。

### 3.2 检索与回答流程

```text
当前 Query（含最近上下文）
  -> Query 重写（可选）
  -> 向量化 + 向量检索
  -> 技能选择与注入
  -> 大模型回答
```

- 检索每轮执行。
- 通过相似度阈值与 `top_k` 控制召回质量。
- 检索后仍可二次筛选，避免无关技能注入。
- 检索 Top-1 技能（需通过 `min_score`）会作为抽取阶段的辅助身份参考输入；抽取内部不再二次检索。

### 3.3 交互抽取策略

- `extract_mode=auto`：每 `extract_turn_limit` 轮尝试抽取。
- `extract_mode=always`：每轮都尝试抽取。
- `extract_mode=never`：关闭自动抽取。
- `/extract_now [hint]`：对当前上下文立即发起后台抽取（别名：`extract_now [hint]`）。
- 对“仅完成一次通用任务且无用户纠偏”的场景（如一次性写报告），应返回不抽取。
- 当用户反馈形成稳定可复用约束（如“不要幻觉”）时，触发抽取或更新。
- 若已有相似用户技能，优先合并更新，而非新建重复技能。

### 3.4 代理服务流程

```text
客户端（OpenAI 兼容请求）
  -> AutoSkill Proxy (/v1/chat/completions)
  -> Query 重写 + 技能检索 + 上下文注入
  -> 上游模型生成
  -> 返回响应给客户端
  -> 异步技能抽取/维护（后台）
```

- 响应时延重点在检索与生成。
- 技能进化异步执行，避免阻塞客户端响应。

## 4. 核心概念

- **Experience**：对话消息或行为事件，是学习信号源。
- **Skill**：可复用能力制品，包含元数据与可执行指令。
- **Skill Candidate**：抽取阶段的临时候选，尚未进入长期库。
- **Maintenance**：新增/合并/丢弃决策与版本管理。
- **Skill Store**：技能制品与向量映射的持久化层。
- **Retrieval Context**：被选中的技能上下文，注入回答链路。

## 5. 本地存储结构（Local Store）

当使用 `store={"provider": "local", "path": "SkillBank"}`：

```text
SkillBank/
  Users/
    <user_id>/
      <skill-slug>/
        SKILL.md
        scripts/          (可选)
        references/       (可选)
        assets/           (可选)
  Common/
    <skill-slug>/SKILL.md
    <library>/<skill-slug>/SKILL.md
  vectors/
    <embedding-signature>.meta.json
    <embedding-signature>.ids.txt
    <embedding-signature>.vecs.f32
```

说明：

- `Users/<user_id>`：用户私有技能。
- `Common/`：共享技能库（通常只读）。
- `vectors/`：按 embedding 签名分开的持久化向量缓存，切换 embedding 模型后不会混用旧索引。

## 6. 仓库结构（更易读版本）

### 6.1 顶层目录

- `autoskill/`：SDK 核心实现。
- `examples/`：可直接运行的示例入口。
- `autoskill/interactive/server.py`：OpenAI 兼容反向代理运行时。
- `OpenClaw-Plugin/`：可本地部署的 OpenClaw 侧车插件（基于 autoskill 接口接入）。
- `web/`：本地 Web UI 静态资源。
- `SkillBank/`：默认本地技能存储根目录。
- `imgs/`：README 示例图片。
- `Dockerfile`：AutoSkill 运行时镜像定义。
- `docker-compose.yml`：Web UI + API Proxy 一键编排部署。

### 6.2 SDK 核心模块

- `autoskill/client.py`：SDK 对外入口（`ingest/search/render/import/export`）。
- `autoskill/config.py`：全局配置模型。
- `autoskill/models.py`：核心数据结构（`Skill`、`SkillHit` 等）。
- `autoskill/render.py`：技能上下文渲染。
- `autoskill/interactive/unified.py`：interactive + proxy 的统一运行时组合入口。

### 6.3 Skill Management 层

- `autoskill/management/extraction.py`：技能抽取逻辑与提示词。
- `autoskill/management/maintenance.py`：新增/合并/丢弃和版本演化。
- `autoskill/management/formats/agent_skill.py`：`SKILL.md` 渲染与解析。
- `autoskill/management/stores/local.py`：目录存储与向量映射。
- `autoskill/management/vectors/flat.py`：本地向量索引后端。
- `autoskill/management/importer.py`：导入外部 Agent Skills。

### 6.4 Interactive 层

- `autoskill/interactive/app.py`：CLI 交互编排。
- `autoskill/interactive/session.py`：Web/API 可复用会话引擎。
- `autoskill/interactive/rewriting.py`：检索 query 重写。
- `autoskill/interactive/selection.py`：注入前技能选择。

### 6.5 示例入口

- `examples/web_ui.py`：本地 Web UI 服务。
- `examples/interactive_chat.py`：终端交互式对话。
- `examples/openai_proxy.py`：OpenAI 兼容代理启动入口。
- `examples/auto_evalution.py`：全自动 LLM-vs-LLM 技能演化评测脚本。
- `examples/basic_ingest_search.py`：离线最小 SDK 流程示例。
- `examples/import_openai_conversations.py`：导入 OpenAI 标准对话并自动抽取技能。

## 7. SDK 最小使用示例

```python
from autoskill import AutoSkill, AutoSkillConfig

sdk = AutoSkill(
    AutoSkillConfig(
        llm={"provider": "mock"},
        embeddings={"provider": "hashing", "dims": 256},
        store={"provider": "local", "path": "SkillBank"},
    )
)

sdk.ingest(
    user_id="u1",
    messages=[
        {"role": "user", "content": "Before each release: run regression -> canary -> monitor -> full rollout."},
        {"role": "assistant", "content": "Understood."},
    ],
)

hits = sdk.search("How should I do a safe release?", user_id="u1", limit=3)
for h in hits:
    print(h.skill.name, h.score)
```

### 7.1 导入 OpenAI 对话并自动抽取技能

```python
from autoskill import AutoSkill, AutoSkillConfig

sdk = AutoSkill(
    AutoSkillConfig(
        llm={"provider": "internlm", "model": "intern-s1-pro"},
        embeddings={"provider": "qwen", "model": "text-embedding-v4"},
        store={"provider": "local", "path": "SkillBank"},
    )
)

result = sdk.import_openai_conversations(
    user_id="u1",
    file_path="./data/openai_dialogues.jsonl",  # 支持 .json 或 .jsonl
    hint="Focus on reusable user preferences and workflows.",
    continue_on_error=True,
    max_messages_per_conversation=100,
)

print("processed:", result["processed"], "upserted:", result["upserted_count"])
for s in result.get("skills", [])[:5]:
    print("-", s.get("name"), s.get("version"))
```

## 8. Provider 配置建议

### 8.1 百炼 DashScope（示例）

```bash
export DASHSCOPE_API_KEY="YOUR_DASHSCOPE_API_KEY"
python3 -m examples.interactive_chat --llm-provider dashscope
```

### 8.2 GLM（BigModel）

```bash
export ZHIPUAI_API_KEY="YOUR_ID.YOUR_SECRET"
python3 -m examples.interactive_chat --llm-provider glm
```

### 8.3 OpenAI / Anthropic

```bash
export OPENAI_API_KEY="YOUR_OPENAI_KEY"
python3 -m examples.interactive_chat --llm-provider openai

export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_KEY"
python3 -m examples.interactive_chat --llm-provider anthropic
```

### 8.4 InternLM（Intern-S1 Pro）

```bash
export INTERNLM_API_KEY="YOUR_INTERNLM_TOKEN"
python3 -m examples.interactive_chat --llm-provider internlm --llm-model intern-s1-pro
```

### 8.5 通用 URL 后端（LLM + Embedding）

```bash
export AUTOSKILL_GENERIC_LLM_URL="http://XXX/v1"
export AUTOSKILL_GENERIC_LLM_MODEL="gpt-5.2"
export AUTOSKILL_GENERIC_EMBED_URL="http://XXX/v1"
export AUTOSKILL_GENERIC_EMBED_MODEL="embd_qwen3"
# 可选（可以为空）：
export AUTOSKILL_GENERIC_API_KEY=""

python3 -m examples.interactive_chat --llm-provider generic --embeddings-provider generic
```

## 9. 常用工作流

### 9.1 终端交互（每轮检索）

```bash
export DASHSCOPE_API_KEY="YOUR_DASHSCOPE_API_KEY"
python3 -m examples.interactive_chat --llm-provider dashscope
```

常用命令：

- `/extract_now [hint]`
- `/extract_every <n>`
- `/extract auto|always|never`
- `/scope user|common|all`
- `/search <query>`
- `/skills`
- `/export <skill_id>`

### 9.2 Web UI

```bash
export INTERNLM_API_KEY="YOUR_INTERNLM_API_KEY"
export DASHSCOPE_API_KEY="YOUR_DASHSCOPE_API_KEY"
python3 -m examples.web_ui --llm-provider internlm --embeddings-provider qwen
```

### 9.3 启动时离线维护（自动执行）

服务启动（`web_ui`、`interactive_chat`、`openai_proxy`）时，AutoSkill 会自动离线执行：
- 检查并补齐本地技能库中 `SKILL.md` 缺失的 `id:`
- 当配置 `AUTOSKILL_AUTO_IMPORT_DIRS` 时，自动导入外部技能目录

可选环境变量：
- `AUTOSKILL_AUTO_NORMALIZE_IDS`（默认 `1`）
- `AUTOSKILL_AUTO_IMPORT_DIRS`（逗号分隔目录）
- `AUTOSKILL_AUTO_IMPORT_SCOPE`（`common`|`user`，默认 `common`）
- `AUTOSKILL_AUTO_IMPORT_LIBRARY`（当 scope=`common` 时的目标库名）
- `AUTOSKILL_AUTO_IMPORT_OVERWRITE`（默认 `0`）
- `AUTOSKILL_AUTO_IMPORT_INCLUDE_FILES`（默认 `1`）
- `AUTOSKILL_AUTO_IMPORT_MAX_DEPTH`（默认 `6`）

### 9.4 OpenAI 兼容代理 API

```bash
export INTERNLM_API_KEY="YOUR_INTERNLM_API_KEY"
export DASHSCOPE_API_KEY="YOUR_DASHSCOPE_API_KEY"
python3 -m examples.openai_proxy --llm-provider internlm --embeddings-provider qwen
```

能力发现：

```bash
curl http://127.0.0.1:9000/v1/autoskill/capabilities
curl http://127.0.0.1:9000/v1/autoskill/openapi.json
```

OpenAI 兼容端点：

- `POST /v1/chat/completions`
- `POST /v1/embeddings`
- `GET /v1/models`

流式聊天示例（`/v1/chat/completions`，SSE）：

```bash
curl -N http://127.0.0.1:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "intern-s1-pro",
    "stream": true,
    "messages": [
      {"role": "user", "content": "请给出 AutoSkill 的 3 点价值。"}
    ]
  }'
```

技能管理端点：

- `GET /v1/autoskill/skills`
- `GET /v1/autoskill/skills/{skill_id}`
- `GET /v1/autoskill/skills/{skill_id}/md`
- `PUT /v1/autoskill/skills/{skill_id}/md`
- `DELETE /v1/autoskill/skills/{skill_id}`
- `POST /v1/autoskill/skills/{skill_id}/rollback`
- `GET /v1/autoskill/skills/{skill_id}/versions`
- `GET /v1/autoskill/skills/{skill_id}/export`
- `POST /v1/autoskill/skills/search`
- `POST /v1/autoskill/skills/import`
- `POST /v1/autoskill/conversations/import`

检索与抽取端点：

- `POST /v1/autoskill/retrieval/preview`
- `POST /v1/autoskill/extractions`
- `POST /v1/autoskill/extractions/simulate`
- `GET /v1/autoskill/extractions/latest`
- `GET /v1/autoskill/extractions`
- `GET /v1/autoskill/extractions/{job_id}`
- `GET /v1/autoskill/extractions/{job_id}/events`（SSE）

### 9.5 自动评测脚本

大规模自动化评测（LLM 用户模拟 + LLM 裁判）：

```bash
python3 -m examples.auto_evalution \
  --mode eval \
  --eval-strategy evolution \
  --base-url http://127.0.0.1:9000 \
  --sim-provider qwen \
  --sim-api-key "$AUTOSKILL_PROXY_API_KEY" \
  --sim-model qwen-plus \
  --judge-provider qwen \
  --judge-model qwen-plus \
  --judge-api-key "$AUTOSKILL_PROXY_API_KEY" \
  --report-json ./proxy_eval_report.json
```

### 9.6 OpenClaw 插件

本地部署侧车服务 + OpenClaw 原生适配器（自动接线）：

```bash
python3 OpenClaw-Plugin/install.py \
  --workspace-dir ~/.openclaw \
  --install-dir ~/.openclaw/plugins/autoskill-openclaw-plugin \
  --adapter-dir ~/.openclaw/extensions/autoskill-openclaw-adapter \
  --llm-provider internlm \
  --llm-model intern-s1-pro \
  --embeddings-provider qwen \
  --embeddings-model text-embedding-v4 \
  --start
```

完整插件说明（安装、接入、运行逻辑、验证）：
- `OpenClaw-Plugin/README.md`

安装脚本会自动：
- 安装 sidecar 运行脚本
- 安装生命周期适配器（`before_agent_start` / `agent_end`）
- 写入 `~/.openclaw/openclaw.json` 的 `plugins.load.paths + plugins.entries`
- 默认启用 `autoskill-openclaw-adapter`

重要：
- 安装完成后，需要重启一次 OpenClaw 运行进程，新的插件配置才会生效。

```bash
openclaw gateway restart
```

如果当前环境没有 `openclaw` CLI，请使用你现有的服务管理方式重启 OpenClaw gateway/runtime 进程。

该插件是技能服务（检索 + 离线进化）。

- `base_url`：`http://127.0.0.1:9100/v1`
- `api_key`：`AUTOSKILL_PROXY_API_KEY` 的值（若未开启鉴权可为空）
- Hook 接口：`POST /v1/autoskill/openclaw/hooks/before_agent_start`
- Hook 接口：`POST /v1/autoskill/openclaw/hooks/agent_end`
- 兼容接口：`POST /v1/autoskill/openclaw/turn`

服务调用示例：

```bash
curl -X POST http://127.0.0.1:9100/v1/autoskill/openclaw/turn \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role":"assistant","content":"你希望什么风格？"},
      {"role":"user","content":"写政府报告，不要表格，避免幻觉。"}
    ],
    "schedule_extraction": true
  }'
```

```bash
curl -X POST http://127.0.0.1:9100/v1/autoskill/conversations/import \
  -H "Content-Type: application/json" \
  -d '{
    "conversations": [
      {"messages":[
        {"role":"user","content":"写一份政策备忘录。"},
        {"role":"assistant","content":"初稿如下..."},
        {"role":"user","content":"更具体，避免幻觉。"}
      ]}
    ]
  }'
```

抽取事件流示例：

```bash
curl -N http://127.0.0.1:9100/v1/autoskill/extractions/<job_id>/events \
  -H "Accept: text/event-stream"
```

向量重建示例：

```bash
curl http://127.0.0.1:9100/v1/autoskill/vectors/rebuild \
  -H "Content-Type: application/json" \
  -d '{
    "user": "u1",
    "scope": "all",
    "force": true,
    "blocking": true
  }'
```

## 10. 项目价值与意义

AutoSkill 把短期交互沉淀为长期能力资产。

- 降低手工编写技能和维护技能的成本。
- 让能力随真实用户反馈持续对齐和升级。
- 支持跨系统迁移与复用，形成可互操作的技能生态。

可以把它理解为：从“提示词工程”走向“经验驱动终身学习 Agent”的一条可落地路径。

## 11. 引用（Citation）

如果你在论文、技术报告或公开演示中使用了 AutoSkill，建议引用：

```bibtex
@software{autoskill_2026,
  author = {Yutao Yang, Junsong Li, Qianjun Pan, Bihao Zhan, Yuxuan Cai, Du Lin, Xin Li, Bo Zhang, Qin Chen, Jie Zhou, Kai Chen, Liang He},
  title = {AutoSkill: Experience-Driven Lifelong Learning via Skill Self-Evolution},
  year = {2026},
  url = {https://github.com/ECNU-ICALK/AutoSkill},
  note = {GitHub repository}
}
```


## 12. 贡献与致谢

机构：上海人工智能实验室、华东师范大学计算机学院

核心作者：杨宇涛

贡献者：李俊松、潘前俊、詹必豪、蔡於轩、杜霖

领衔作者：周杰、陈恺、贺樑

学术指导：李鑫、张铂、陈琴
