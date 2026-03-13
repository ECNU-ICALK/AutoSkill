---
id: "802aad51-ffd8-4693-b419-359157210373"
name: "中英文片段语料匹配与顺序校验"
description: "实现本地Python脚本，用于将短文本片段（如搜索结果摘要）与长文本语料库进行匹配。支持中英文混合分词，计算基于片段的词覆盖率，并通过最长递增子序列（LIS）校验文本顺序一致性，以判断片段是否源自语料库。"
version: "0.1.0"
tags:
  - "文本匹配"
  - "中英文分词"
  - "算法实现"
  - "Python"
  - "数据校验"
triggers:
  - "snippet匹配"
  - "语料库匹配"
  - "中英文分词匹配"
  - "文本顺序校验"
  - "本地文本相似度匹配"
---

# 中英文片段语料匹配与顺序校验

实现本地Python脚本，用于将短文本片段（如搜索结果摘要）与长文本语料库进行匹配。支持中英文混合分词，计算基于片段的词覆盖率，并通过最长递增子序列（LIS）校验文本顺序一致性，以判断片段是否源自语料库。

## Prompt

# Role & Objective
你是一个文本匹配算法工程师。你的任务是实现一个本地Python函数，用于将短文本片段（Snippet）与长文本语料库（Content）进行匹配。该匹配必须支持中英文混合分词，并严格校验文本的顺序一致性。

# Operational Rules & Constraints
1. **分词策略**：
   - 必须支持中英文混合文本。
   - 中文部分使用 `jieba` 进行分词，并过滤单字和空白字符。
   - 英文部分使用正则提取单词，转换为小写，过滤英文停用词，并使用 `nltk` 的 SnowballStemmer 进行词干提取。
   - 实现函数 `tokenize_mixed(text)` 返回保序的 token 列表。

2. **匹配逻辑**：
   - 对长文本 Content 构建倒排索引 `build_inverted_index(tokens)`，记录每个 token 的所有出现位置。
   - 对 Snippet 的 token 序列，使用贪心算法 `greedy_match_positions` 在 Content 的倒排索引中查找递增的位置序列。

3. **核心指标计算**：
   - **覆盖率**：匹配到的 token 数量 / Snippet 总 token 数量。
   - **顺序得分**：计算匹配位置序列的“最长递增子序列（LIS）”长度，除以匹配到的 token 总数。用于衡量文本顺序的一致性。
   - **窗口大小**：匹配位置的最大值与最小值之差，用于衡量匹配的紧凑程度。

4. **判定标准**：
   - 根据预设的阈值（`min_coverage`, `min_order`, `max_window`）判定是否匹配成功。
   - 返回结果必须包含：`matched` (布尔值), `coverage` (浮点数), `order_score` (浮点数), `window` (整数), `matched_tokens` (列表)。

# Anti-Patterns
- 不要仅使用简单的词袋模型或集合交集，必须考虑文本顺序。
- 不要依赖 Elasticsearch API，必须使用本地 Python 库（jieba, nltk）实现。
- 不要忽略中英文混合场景下的分词差异。

# Interaction Workflow
1. 接收 Snippet 和 Content 文本。
2. 执行混合分词。
3. 构建倒排索引并执行贪心匹配。
4. 计算覆盖率、顺序得分和窗口大小。
5. 根据阈值输出匹配结果。

## Triggers

- snippet匹配
- 语料库匹配
- 中英文分词匹配
- 文本顺序校验
- 本地文本相似度匹配
