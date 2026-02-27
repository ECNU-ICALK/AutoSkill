# AutoSkill OpenClaw 插件

`AutoSkill-OpenClaw-Plugin` 是一个本地 sidecar 服务，用于将 AutoSkill 接入 OpenClaw，实现：

- 技能检索（`query rewrite + retrieval`）
- 异步技能进化（`extract + add/merge/discard`）

## 1. 仓库与本地路径

- GitHub 源码：
- [https://github.com/ECNU-ICALK/AutoSkill/tree/main/OpenClaw-Plugin](https://github.com/ECNU-ICALK/AutoSkill/tree/main/OpenClaw-Plugin)

- 仓库内 sidecar 元数据清单：
- `OpenClaw-Plugin/sidecar.manifest.json`

- 运行时安装目录（安装脚本自动创建）：
- `~/.openclaw/plugins/autoskill-openclaw-plugin`

- OpenClaw 原生适配器目录（自动安装）：
- `~/.openclaw/extensions/autoskill-openclaw-adapter`

- OpenClaw 配置文件（安装脚本自动更新）：
- `~/.openclaw/openclaw.json`

- 技能存储目录（默认）：
- `~/.openclaw/autoskill/SkillBank`

## 2. 功能特性

- Hook 风格检索接口：
- `POST /v1/autoskill/openclaw/hooks/before_agent_start`

- Hook 风格后处理进化接口：
- `POST /v1/autoskill/openclaw/hooks/agent_end`

- 向后兼容的单轮接口：
- `POST /v1/autoskill/openclaw/turn`

- 后台抽取/进化接口：
- `POST /v1/autoskill/extractions`
- `GET /v1/autoskill/extractions/latest`
- `GET /v1/autoskill/extractions`
- `GET /v1/autoskill/extractions/{job_id}`
- `GET /v1/autoskill/extractions/{job_id}/events`

- 离线会话导入接口：
- `POST /v1/autoskill/conversations/import`

- 技能管理接口：
- `POST /v1/autoskill/skills/search`
- `GET /v1/autoskill/skills`
- `GET /v1/autoskill/skills/{skill_id}`
- `PUT /v1/autoskill/skills/{skill_id}/md`
- `DELETE /v1/autoskill/skills/{skill_id}`
- `POST /v1/autoskill/skills/{skill_id}/rollback`

## 3. 运行流程

推荐的 Hook 生命周期如下：

1. OpenClaw 调用 `before_agent_start`。
2. 服务端执行（可选）query rewrite，并检索技能，返回检索结果载荷（`selected_skills`、`context`、`context_message`、元数据）。
3. 适配器基于检索结果组装标准化 prompt 块，前置注入到模型输入，并提示模型忽略与当前任务不相关的技能。
4. OpenClaw 在任务结束时调用 `agent_end`，并可附带成功信号。
5. 服务端后台调度抽取任务，更新 `SkillBank`。

说明：
- `agent_end` 支持成功门控（`success` / `task_success` / `objective_met`）。
- 现有 `/v1/autoskill/openclaw/turn` 仍可用于单接口集成。
- 安装脚本会自动把 adapter 路径和插件条目写入 `~/.openclaw/openclaw.json`，无需手工接线。
- 若 `openclaw.json` 不是合法 JSON，安装脚本会停止，不会覆盖文件。
- 适配器优先使用 OpenClaw 原生 `registerHook` 注册，若不可用则回退到 `on`，保证兼容。

## 4. 前置依赖

- Python 3.10+
- 本地可访问 AutoSkill 仓库
- 插件 `.env`（或系统环境变量）中配置了可用的 LLM 与 embedding 凭据

## 5. 安装

### 方式 A：从 GitHub 源码安装

```bash
git clone https://github.com/ECNU-ICALK/AutoSkill.git
cd AutoSkill
python3 -m pip install -e .
python3 OpenClaw-Plugin/install.py \
  --workspace-dir ~/.openclaw \
  --install-dir ~/.openclaw/plugins/autoskill-openclaw-plugin \
  --adapter-dir ~/.openclaw/extensions/autoskill-openclaw-adapter \
  --repo-dir "$(pwd)" \
  --llm-provider internlm \
  --llm-model intern-s1-pro \
  --embeddings-provider qwen \
  --embeddings-model text-embedding-v4
```

### 方式 B：从已有本地路径安装

```bash
cd /path/to/AutoSkill
python3 -m pip install -e .
python3 OpenClaw-Plugin/install.py \
  --workspace-dir ~/.openclaw \
  --install-dir ~/.openclaw/plugins/autoskill-openclaw-plugin \
  --adapter-dir ~/.openclaw/extensions/autoskill-openclaw-adapter \
  --repo-dir "$(pwd)" \
  --llm-provider internlm \
  --llm-model intern-s1-pro \
  --embeddings-provider qwen \
  --embeddings-model text-embedding-v4
```

安装后会生成：

- `~/.openclaw/plugins/autoskill-openclaw-plugin/.env`
- `~/.openclaw/plugins/autoskill-openclaw-plugin/run.sh`
- `~/.openclaw/plugins/autoskill-openclaw-plugin/start.sh`
- `~/.openclaw/plugins/autoskill-openclaw-plugin/stop.sh`
- `~/.openclaw/plugins/autoskill-openclaw-plugin/status.sh`
- `~/.openclaw/extensions/autoskill-openclaw-adapter/index.js`
- `~/.openclaw/extensions/autoskill-openclaw-adapter/openclaw.plugin.json`
- `~/.openclaw/extensions/autoskill-openclaw-adapter/package.json`
- `~/.openclaw/openclaw.json`（会更新：`plugins.load.paths` 与 `plugins.entries.autoskill-openclaw-adapter`）

## 6. 启动方式

### 流程 A：安装一次，然后独立启动 sidecar

1. 编辑插件环境变量：

```bash
vim ~/.openclaw/plugins/autoskill-openclaw-plugin/.env
```

通常必填：

- `INTERNLM_API_KEY`（或你选择的 LLM 提供方 key）
- `DASHSCOPE_API_KEY`（若使用 qwen embedding）
- `AUTOSKILL_PROXY_API_KEY`（可选）

2. 启动服务：

```bash
~/.openclaw/plugins/autoskill-openclaw-plugin/start.sh
~/.openclaw/plugins/autoskill-openclaw-plugin/status.sh
```

3. 验证服务：

```bash
curl http://127.0.0.1:9100/health
curl http://127.0.0.1:9100/v1/autoskill/capabilities
```

4. 重启 OpenClaw 运行时，加载 `~/.openclaw/openclaw.json` 中的新插件配置：

```bash
openclaw gateway restart
```

如果当前环境没有 `openclaw` CLI，请使用你现有的服务管理方式重启 OpenClaw gateway/runtime 进程。

5. （可选）检查 adapter 配置是否已写入：

```bash
cat ~/.openclaw/openclaw.json
```

应包含：
- `plugins.load.paths` 包含 `~/.openclaw/extensions/autoskill-openclaw-adapter`
- `plugins.entries.autoskill-openclaw-adapter.enabled = true`
- `plugins.entries.autoskill-openclaw-adapter.config.baseUrl = http://127.0.0.1:9100/v1`
- 若 sidecar 开启鉴权，需设置 `plugins.entries.autoskill-openclaw-adapter.config.apiKey`
  或在 OpenClaw 运行环境中提供 `AUTOSKILL_PROXY_API_KEY`。

### 流程 B：一条命令安装并启动

```bash
python3 OpenClaw-Plugin/install.py \
  --workspace-dir ~/.openclaw \
  --install-dir ~/.openclaw/plugins/autoskill-openclaw-plugin \
  --adapter-dir ~/.openclaw/extensions/autoskill-openclaw-adapter \
  --repo-dir "$(pwd)" \
  --llm-provider internlm \
  --llm-model intern-s1-pro \
  --embeddings-provider qwen \
  --embeddings-model text-embedding-v4 \
  --start
```

然后验证：

```bash
curl http://127.0.0.1:9100/health
```

重要：
- 安装/启动完成后，需要重启一次 OpenClaw 运行时，否则 adapter 的 hook 配置可能尚未生效。

```bash
openclaw gateway restart
```

如果不希望自动修改 OpenClaw 配置：

```bash
python3 OpenClaw-Plugin/install.py --skip-openclaw-config-update
```

## 7. OpenClaw 调用示例

### 7.1 Hook：before_agent_start（检索 + 上下文注入载荷）

```bash
curl -X POST http://127.0.0.1:9100/v1/autoskill/openclaw/hooks/before_agent_start \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role":"user","content":"Write a government report. No table. Avoid hallucinations."}
    ]
  }'
```

响应包含：

- `hits` / `selected_for_context_ids`
- `context`
- `context_message`（adapter 兼容字段；adapter 会基于 `buildPromptFromData` 组装最终注入 prompt）

### 7.2 Hook：agent_end（异步抽取/进化）

```bash
curl -X POST http://127.0.0.1:9100/v1/autoskill/openclaw/hooks/agent_end \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role":"user","content":"Write a government report. No table. Avoid hallucinations."},
      {"role":"assistant","content":"Draft report ..."},
      {"role":"user","content":"Make it sharper and more specific."},
      {"role":"assistant","content":"Updated draft ..."}
    ],
    "success": true,
    "user_feedback": "Good, keep this writing policy for next time."
  }'
```

### 7.3 兼容模式：单轮接口

```bash
curl -X POST http://127.0.0.1:9100/v1/autoskill/openclaw/turn \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role":"assistant","content":"How should I write it?"},
      {"role":"user","content":"Write a government report. No table. Avoid hallucinations."}
    ],
    "schedule_extraction": true
  }'
```

### 7.4 离线会话导入

```bash
curl -X POST http://127.0.0.1:9100/v1/autoskill/conversations/import \
  -H "Content-Type: application/json" \
  -d '{
    "conversations": [
      {
        "messages": [
          {"role":"user","content":"Write a policy memo."},
          {"role":"assistant","content":"Draft ..."},
          {"role":"user","content":"More specific and avoid hallucinations."}
        ]
      }
    ]
  }'
```

### 7.5 抽取事件流

```bash
curl -N http://127.0.0.1:9100/v1/autoskill/extractions/<job_id>/events \
  -H "Accept: text/event-stream"
```

## 8. User ID 路由

User ID 解析顺序：

1. 请求体 `user`
2. 请求头 `X-AutoSkill-User`
3. `Authorization: Bearer <JWT>` 的 payload 字段 `id`
4. 回退 `AUTOSKILL_USER_ID`

## 9. 生命周期命令

```bash
~/.openclaw/plugins/autoskill-openclaw-plugin/start.sh
~/.openclaw/plugins/autoskill-openclaw-plugin/status.sh
~/.openclaw/plugins/autoskill-openclaw-plugin/stop.sh
```

日志文件：

- `~/.openclaw/plugins/autoskill-openclaw-plugin/autoskill-openclaw-plugin.log`

## 10. 关键环境变量

- `AUTOSKILL_PROXY_HOST`（默认 `127.0.0.1`）
- `AUTOSKILL_PROXY_PORT`（默认 `9100`）
- `AUTOSKILL_STORE_DIR`（默认 `~/.openclaw/autoskill/SkillBank`）
- `AUTOSKILL_LLM_PROVIDER` / `AUTOSKILL_LLM_MODEL`
- `AUTOSKILL_EMBEDDINGS_PROVIDER` / `AUTOSKILL_EMBEDDINGS_MODEL`
- `AUTOSKILL_REWRITE_MODE`（`never|auto|always`）
- `AUTOSKILL_SKILL_SCOPE`（`user|library|all`）
- `AUTOSKILL_MIN_SCORE` / `AUTOSKILL_TOP_K`
- `AUTOSKILL_INGEST_WINDOW`
- `AUTOSKILL_EXTRACT_ENABLED`
- `AUTOSKILL_PROXY_API_KEY`（可选）
- `AUTOSKILL_DOTENV`（可选；adapter 预加载 dotenv 路径，支持分号/逗号分隔）
- `AUTOSKILL_MAX_INJECTED_CHARS`（可选；adapter 端注入 prompt 最大字符数）
