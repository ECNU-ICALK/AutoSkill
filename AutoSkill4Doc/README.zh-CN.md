# AutoSkill4Doc

[English](README.md) | 中文

`AutoSkill4Doc` 是仓库内独立的离线文档抽取与技能编译引擎。
它通过明确的离线阶段把文档转换为可执行技能，并保留来源追踪、
版本历史与可增量重跑能力。

## 范围

当前主流程：

```text
document
  -> ingest_document（DocumentRecord + TextUnit + StrictWindow）
  -> extract_skills（SupportRecord + SkillDraft）
  -> compile_skills（SkillSpec）
  -> register_versions
  -> registry + staging 快照 + 最终 SkillBank store + 可见父子技能树
```

核心分层：

1. `DocumentRecord`
2. `TextUnit`
3. `StrictWindow`
4. `SupportRecord`
5. `SkillDraft`
6. `SkillSpec`

## 核心能力

- 独立 CLI：`autoskill4doc ...` 或 `python -m AutoSkill4Doc ...`
- 基于 `content_hash` 的增量跳过
- section 过滤、对话段裁剪、strict/recommended 窗口切分
- 支持 dry-run 和分阶段执行
- 支持 provenance/change log/version history
- 支持生命周期状态：`candidate -> draft -> evaluating -> active -> watchlist -> deprecated -> retired`
- 支持在文档技能库根目录下生成 `总技能/子技能/references` 可见树
- 非 `dry-run` 构建过程中会把中间结果写到 `.runtime/intermediate_runs/<run_id>/`
- 支持通过内置或自定义 YAML 配置技能 taxonomy，`domain_type` 由调用方显式提供，不由模型预测

输入说明：
- `text / markdown / json / jsonl` 可直接读取
- `.doc / .docx` 依赖本地转换工具，例如 `textutil`、`antiword`、`catdoc`
- 图片、PDF 等当前不支持直接解析，会被跳过而不是作为乱码文本导入
- `generic` LLM / embedding 后端需要显式设置 `AUTOSKILL_GENERIC_LLM_URL` / `AUTOSKILL_GENERIC_EMBED_URL`
- 已导出的可见技能树产物（`总技能/`、`子技能/`、`references/`）在 ingest 时会被自动跳过，避免把生成后的技能再次当作原始文档抽取

## 默认路径

默认库目录：

```text
<repo_root>/SkillBank/DocSkill/
```

默认 registry 路径：

```text
<store_root>/.runtime/document_registry/
```

默认中间结果路径：

```text
<store_root>/.runtime/intermediate_runs/
```

可见输出结构：

```text
<store_root>/
  README.md
  <family_name>/
    总技能/
      SKILL.md
      references/
        children_manifest.json
        children_map.md
    子技能/
      <child_name>/
        SKILL.md
        references/
          evidence.md
          evidence_manifest.json
  .runtime/
    document_registry/
    intermediate_runs/
    staging/
    library_manifest.json
```

同一个库根目录下现在有 3 层存储：

1. `.runtime/document_registry/`
   - 内部 document / support / skill / version 记录
2. `Users/<internal_user>/`
   - 经过 maintainer 整理后的最终 AutoSkill 本地 store 技能
3. `<family_name>/`
   - 面向浏览和导出的可见父子技能树投影

它们共用同一个根目录，但不是同一份数据。对于长任务，非 `dry-run`
构建还会把阶段快照持续写到 `.runtime/intermediate_runs/<run_id>/`。

## 总技能 / 子技能是如何生成的

当前实现不是直接从文档一次性吐出一个“总技能目录树”，而是分两层：

1. 先把文档抽成 `SkillSpec`
   - `ingest` 负责把文档切成 `StrictWindow`
   - `extract` 负责从 window 提取 `SupportRecord + SkillDraft`
   - `compile` 负责把 draft 归一成 `SkillSpec`
   - `register_versions` 负责做 registry 持久化和版本状态处理

2. 再把结果投影成可见父子结构
   - 如果最终 store skill 已存在，可见子技能会优先按 `Users/<internal_user>/...` 里的最终技能重建
   - 证据文件：`references/evidence.md` 和 `references/evidence_manifest.json` 仍由 registry 中关联的 `SupportRecord + DocumentRecord` 拼接
   - 总技能：按同一个 `family_name` 下的全部子技能自动合成 `总技能/SKILL.md`
   - 索引文件：同时生成 `children_manifest.json` 和 `children_map.md`

这种实现的好处是：

- 原始真相仍然保留在 registry 的 document / support / skill 层，不是只有一个最终 `SKILL.md`
- `总技能` 只是导航层，不会反过来污染原始 skill 事实
- 子技能更新后，可以整体重建同一家族的可见树，避免目录漂移
- 现在可见树会优先对齐最终 store skill，因此会尽量和 `Users/<internal_user>/...` 保持一致

当前要稳定得到你想要的目录结构，最重要的是构建时显式传：

- `--family-name`

其中 `--family-name` 最关键，因为它直接决定顶层目录名，例如 `认知行为疗法/`。
如果不传 `--profile-id`，系统会基于 taxonomy 和 `family_name` 自动派生；
如果不传 `--taxonomy-axis`，则会优先使用 taxonomy 配置里的默认值。
`--user-id` 现在只是内部 store 路由细节，不再是正常文档抽取流程里需要关心的主参数。

## Skill Taxonomy

`AutoSkill4Doc` 内部仍然保持一组稳定的 `asset_type`，供 compile / versioning 使用：

- `macro_protocol`
- `session_skill`
- `micro_skill`
- `safety_rule`
- `knowledge_reference`

在这层之上，可以通过 taxonomy 配置给出领域自己的标签和别名：

- 内置 taxonomy：`--domain-type psychology` / `--domain-type chemistry`
- 自定义 taxonomy：`--skill-taxonomy /path/to/taxonomy.yaml`

注意：

- `domain_type` 是用户或调用方已知的配置输入，不是模型预测结果
- 模型最终仍返回内部稳定的 `asset_type`
- taxonomy 文件除了提供领域标签、别名和提示词引导，还可以同时提供：
  - 默认 `family_name`
  - 默认 `taxonomy_axis`
  - family 候选集合（供后续受约束的 family 判定使用）

示例：

```bash
python3 -m AutoSkill4Doc llm-extract \
  --file ./chem_docs \
  --domain chemistry \
  --domain-type chemistry \
  --family-name "分析化学" \
  --skill-taxonomy ./custom-taxonomy.yaml \
  --store-path ./SkillBank/DocSkill
```

## 配置文件说明

当前 `AutoSkill4Doc` 的配置主要来自 3 层：

1. 内置 taxonomy 文件
   - [AutoSkill4Doc/skill_taxonomies/default.yaml](/Users/jiezhou/Desktop/工作/其他/浦江/AutoSkill/AutoSkill4Doc/skill_taxonomies/default.yaml)
   - [AutoSkill4Doc/skill_taxonomies/psychology.yaml](/Users/jiezhou/Desktop/工作/其他/浦江/AutoSkill/AutoSkill4Doc/skill_taxonomies/psychology.yaml)
   - [AutoSkill4Doc/skill_taxonomies/chemistry.yaml](/Users/jiezhou/Desktop/工作/其他/浦江/AutoSkill/AutoSkill4Doc/skill_taxonomies/chemistry.yaml)
2. 用户通过 `--skill-taxonomy` 传入的自定义 taxonomy 文件
3. 运行时 CLI 参数与 provider 环境变量

taxonomy 的加载顺序是：

- 总是先加载 `default.yaml`
- 如果传了 `--domain-type psychology` / `chemistry`，再把对应内置 taxonomy 叠加到 `default.yaml` 上
- 如果传了 `--skill-taxonomy /path/to/file.yaml`，则用这个自定义文件作为 overlay，替代内置 domain 文件
- 最终解析后的结果会用于：
  - 抽取 prompt 的领域提示
  - `asset_type` 别名归一化
  - 默认 `family_name`
  - 默认 `taxonomy_axis`
  - 自动派生 `profile_id`

taxonomy 里几个最重要的字段：

- `taxonomy_id`：稳定 taxonomy 标识，用于派生 `profile_id`
- `domain_type`：调用方显式指定的领域类型名
- `display_name`：展示名称
- `default_base_type`：默认内部 `asset_type`
- `family_axis`：默认可见分类轴，例如 `疗法`、`实验路线`
- `default_family_name`：默认 family 名称
- `family_candidates`：可选 family 候选集合，供后续受约束判定使用
- `asset_types`：领域标签到内部稳定 base type 的映射

最小 taxonomy 示例：

```yaml
taxonomy_id: psychology
domain_type: psychology
display_name: Psychology
default_base_type: session_skill
family_axis: 疗法
default_family_name: 通用心理咨询
family_candidates:
  - id: cbt
    name: CBT（认知行为疗法）
    aliases: ["CBT", "认知行为疗法", "cognitive behavioral therapy"]
asset_types:
  - base_type: session_skill
    label: session_intervention
    description: One counseling workflow or session scaffold.
    aliases: ["session_intervention", "session_skill"]
```

其他配置入口：

- [AutoSkill4Doc/core/config.py](/Users/jiezhou/Desktop/工作/其他/浦江/AutoSkill/AutoSkill4Doc/core/config.py)
  - 代码默认值，例如默认 store 路径、runtime 路径、extract strategy
- [AutoSkill4Doc/core/provider_config.py](/Users/jiezhou/Desktop/工作/其他/浦江/AutoSkill/AutoSkill4Doc/core/provider_config.py)
  - `dashscope`、`glm`、`openai`、`anthropic`、`generic` 的 provider/env 解析

provider 配置不是文件，而是环境变量。常用项包括：

- DashScope：`DASHSCOPE_API_KEY`，可选 `DASHSCOPE_MODEL`、`DASHSCOPE_EMBED_MODEL`
- GLM：`ZHIPUAI_API_KEY` 或 `BIGMODEL_API_KEY`
- Generic backend：`AUTOSKILL_GENERIC_LLM_URL`、`AUTOSKILL_GENERIC_EMBED_URL`

解析优先级：

- 显式 CLI 参数
- 自定义 taxonomy 文件
- 内置 taxonomy 文件
- `core/config.py` 中的代码默认值
- provider 的环境变量（用于认证和 endpoint URL）

## 流程是否合理

按当前版本来看，这个流程作为最小可运行版本是合理的：

- 抽取主链路和可见目录生成解耦
- `总技能/子技能` 是落盘投影，不是新的“真相层”
- 重新同步目录时以最终 store 结果为主、以 registry 证据为辅，能避免人工目录漂移

但它和 paper 目标相比，仍然是一个简化版：

- 现在的 `总技能` 是基于当前有效子技能自动汇总出来的
- 还没有完整实现 paper 里的 `single-document standardization + canonical merge + parent synthesis` 全链路
- 所以目录结构已经对齐了，但“子技能如何合并成 canonical child”的治理强度还没完全到 paper 那个版本
- `.runtime/document_registry/` 里当前仍可能保留比最终 `Users/<internal_user>/...` 和 `<family_name>/...` 更多的内部 skill 记录

如果你的当前优先级是“先保证输出长得对”，这版已经够用。  
如果你的优先级是“保证和 paper 一样的归并质量”，下一步要继续补 canonical merge 那一段。

落盘对象：

- `documents`
- `supports`
- `skills`
- `lifecycles`
- `version_history`
- `change_logs`
- `provenance_links`

## CLI

独立 CLI：

```bash
python3 -m AutoSkill4Doc build --file ./paper.md --dry-run
python3 -m AutoSkill4Doc llm-extract --file ./cbt_docs --family-name "认知行为疗法"
python3 -m AutoSkill4Doc ingest --file ./docs/ --json
python3 -m AutoSkill4Doc extract --file ./paper.md --json
autoskill4doc compile --file ./paper.md --json
python3 -m AutoSkill4Doc diag --file ./paper.md --report-path ./diag.jsonl --json
python3 -m AutoSkill4Doc retrieve-hierarchy --store-path ./SkillBank/DocSkill --profile-id psychology::认知行为疗法 --family-name "认知行为疗法" --json
python3 -m AutoSkill4Doc canonical-merge --store-path ./SkillBank/DocSkill --profile-id psychology::认知行为疗法 --family-name "认知行为疗法" --child-type intake --json
python3 -m AutoSkill4Doc migrate-layout --store-path ./SkillBank/DocSkill --json

python3 -m AutoSkill4Doc build \
  --file ./cbt_docs/ \
  --domain psychology \
  --domain-type psychology \
  --family-name "认知行为疗法" \
  --store-path ./SkillBank/DocSkill
```

说明：
- `dry-run` 会跑 ingest/extract/compile 供你查看结果，但不会写入最终 registry / skill store / 可见技能树。
- `diag` 始终以 dry-run 观察模式运行，不会写入 registry 或 skill store。
- 非 `dry-run` 的 `build / llm-extract` 会把 ingest / extract / compile / register 的阶段快照写到 `.runtime/intermediate_runs/<run_id>/`。
- `canonical-merge` 当前用于查看 staging 结果，必须显式传 `--profile-id` 和 `--family-name`。

## Python API

```python
from AutoSkill4Doc import extract_from_doc

result = extract_from_doc(
    sdk=sdk,
    file_path="./paper.md",
    domain="psychology",
    domain_type="psychology",
    family_name="认知行为疗法",
    dry_run=True,
)
```

分阶段调用：

```python
from AutoSkill4Doc.pipeline import build_default_document_pipeline

pipeline = build_default_document_pipeline(sdk=sdk)
ingest = pipeline.ingest_document(file_path="./paper.md", dry_run=True)
print(len(ingest.windows))
extracted = pipeline.extract_skills(documents=ingest.documents, windows=ingest.windows)
compiled = pipeline.compile_skills(
    skill_drafts=extracted.skill_drafts,
    support_records=extracted.support_records,
)
```

## 模块结构

- `extract.py` / `__main__.py`：独立包 CLI + API 入口
- `pipeline.py`：分阶段编排
- `ingest.py`：文档归一化与增量检测
- `taxonomy.py`：内置/自定义 skill taxonomy 加载，以及 `family_name` / `profile_id` 解析
- `document/file_loader.py`：目录/文件读取、转换兜底与生成产物跳过
- `document/windowing.py`：section 过滤与 strict/recommended 窗口构造
- `stages/extractor.py`：`DocumentRecord -> SupportRecord[] + SkillDraft[]`
- `stages/compiler.py`：`SkillDraft[] -> SkillSpec[]`
- `stages/diag.py`：基于现有抽取链路的 dry-run 诊断报告
- `stages/hierarchy.py`：manifest 优先的可见层级浏览/检索
- `stages/merge.py`：基于 staging 的 canonical merge 结果查看
- `stages/migrate.py`：安全的 `.runtime` 布局准备与迁移检查
- `store/versioning.py`：基于 skill identity 的版本与生命周期治理
- `store/registry.py`：文件系统 registry 持久化
- `store/visible_tree.py`：基于最终 store skill 与 registry 证据导出的可见 `总技能/子技能/references`
- `store/intermediate.py`：按运行批次持续写入 ingest/extract/compile/register 中间快照
- `store/layout.py`：共享的 visible/runtime 路径约定
- `store/staging.py`：canonical merge staging 读写辅助
- `core/config.py`：AutoSkill4Doc 独立默认路径与配置
- `core/provider_config.py`：独立 provider 配置辅助
- `models.py`：核心数据模型
- `prompts.py`：offline prompt 构造与运行时 prompt 替换

## 迁移说明

- 已替代旧目录 `autoskill/offline/document/`。
- 文档抽取现在直接通过 `AutoSkill4Doc` 运行，不再通过 `autoskill/offline` 路由。
- 推荐入口是 `python -m AutoSkill4Doc`；`extract.py` 作为该 CLI 的实现模块保留。
