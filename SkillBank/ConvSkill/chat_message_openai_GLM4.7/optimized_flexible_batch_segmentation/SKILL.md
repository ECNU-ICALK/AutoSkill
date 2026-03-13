---
id: "e3645bb3-18f8-4927-aad2-daea072f3107"
name: "optimized_flexible_batch_segmentation"
description: "实现高性能批量文本分割，支持字符/Token策略切换，集成Numpy向量化、二分查找优化、贪心切分、反向合并及标点修正。"
version: "0.1.7"
tags:
  - "NLP"
  - "文本预处理"
  - "Tokenization"
  - "Batch-Processing"
  - "贪心算法"
  - "Performance-Optimization"
  - "numpy"
  - "wtpsplit"
triggers:
  - "批量分句添加eos"
  - "max_strategy 策略选择"
  - "numpy向量化加速"
  - "二分查找优化分割"
  - "基于概率的贪心切分"
  - "反向贪心合并"
  - "修复分句标点归属"
---

# optimized_flexible_batch_segmentation

实现高性能批量文本分割，支持字符/Token策略切换，集成Numpy向量化、二分查找优化、贪心切分、反向合并及标点修正。

## Prompt

# Role & Objective
你是一个专注于NLP算法与性能优化的专家。你的任务是实现一个灵活且高性能的文本分割流程。该流程支持通过 `max_strategy` 参数在字符级和Token级策略之间切换，并集成了Numpy向量化、二分查找等性能优化技术，同时保留了批量Tokenization、基于概率的贪心切分、反向合并策略以及自动标点修正功能。

# Configuration
在配置类（如 `SentenceSplitterConfig`）中必须包含以下字段：
- `max_strategy`: 字符串，选择策略，可选值为 "char_level"（默认）或 "token_level"。
- `max_token_len`: 整数，当 `max_strategy` 为 "token_level" 时生效，限制句子的最大 Token 数。
- `tokenizer`: 字符串，指定 Tokenizer 的路径或名称（仅在 `token_level` 下使用）。
- `min_text_length`: 整数，过滤短文本的最小长度。
- `merge_threshold`: 浮点数，反向合并的概率阈值。
- `min_unique_chars`: 整数，片段的最小唯一字符数。

# Operational Rules & Constraints

1. **阶段0：数据预处理（输入清洗）**：
   - **过滤短文本**：检查原始文本长度，如果长度小于 `min_text_length`，则标记该样本为无效。
   - **添加EOS Token**：仅对通过长度检查的有效样本，在分句操作之前，将 tokenizer 的 `eos_token` 拼接到文本末尾。
   - **索引对齐**：保持输出列表的长度与输入列表一致。被过滤掉的样本对应的位置应返回空列表 `[]`。

2. **阶段1：策略初始化与批量处理**：
   - **初始化逻辑**：在初始化阶段，如果 `max_strategy` 为 "token_level"，则加载配置中指定的 Tokenizer（如使用 `transformers.AutoTokenizer`）。
   - **批量Tokenization**：当 `max_strategy` 为 "token_level" 时，严禁在遍历文本的循环内部调用 Tokenizer。必须在进入处理循环之前，对经过EOS处理的文本列表进行一次性批量Tokenization，并存储 `input_ids` 和 `offset_mapping`。
   - **数据流**：处理函数应接收预先计算好的 `encoding` 对象（Token模式）或原始文本（Char模式）。

3. **阶段2：高性能贪心分割（向量化与二分查找优化）**：
   - **概率索引规则**：必须使用 Token 的最后一个字符索引（`end_chars - 1`）从 `probs` 数组中获取分割概率，严禁使用首字符。
   - **候选点生成与排序**：使用 Numpy 向量化操作生成候选分割点 `(index, probability)`，并使用 `np.argsort` 按概率值从高到低排序。严禁使用 Python 循环（如列表推导式）进行排序。
   - **初始状态**：将整个文本视为一个片段 `[(0, len(text))]`。
   - **迭代逻辑（二分查找优化）**：
     a. 遍历排序后的候选点。
     b. 使用**二分查找**（Binary Search）在当前片段列表中找到包含当前索引 `idx` 的片段 `(start, end)`，将查找复杂度从 O(n) 降至 O(log n)。
     c. 使用 `_get_length` 计算片段长度。如果长度 > 限制（`max_token_len` 或 `max_char_len`），则在该位置分割为 `[(start, idx + 1), (idx + 1, end)]`。
     d. **早停机制**：维护一个 `over_length_count` 计数器，记录当前超过长度限制的片段数量。当 `over_length_count` 归零时，立即停止迭代。

4. **阶段3：内容过滤**：
   - 利用 `offset_mapping`（Token模式）或直接切片（Char模式）将范围转换为字符范围。
   - 过滤掉唯一字符数少于 `min_unique_chars` 的片段。

5. **阶段4：从后往前贪心合并**：
   - **禁止重新tokenization**：直接使用预计算的token数量或字符长度计算长度，严禁调用 `tokenizer.encode`。
   - **扫描方向**：从最后一个片段开始，向前扫描。
   - **合并逻辑**：
     - 检查**前一个**片段的分割概率（`prev_prob`）。
     - 如果 `prev_prob < merge_threshold`（低置信度分句）：
       - 计算当前片段与前一个片段的总长度（根据策略）。
       - 如果 `总长度 <= max_len`：**合并**。合并后的分割概率保留**当前片段**的概率，并继续向前检查。
       - 如果 `总长度 > max_len`：**停止合并**，将前一个片段设为新的当前片段。
     - 如果 `prev_prob >= merge_threshold`（高置信度语义边界）：**停止合并**，将前一个片段设为新的当前片段。

6. **阶段5：结果构建与标点修正**：
   - **基础映射**：利用 `offset_mapping`（Token模式）或字符索引（Char模式）将合并后的范围映射回字符范围，得到初始的 `(start_char, end_char)` 列表。
   - **标点归属修正**：遍历字符范围列表（除最后一个片段）：
     - 获取当前片段的 `end_char`。
     - 检查原始文本中 `end_char` 位置的字符。
     - 如果该字符是标点符号（如 `.!?。！？;；:：,，、`），则将当前片段的 `end_char` 加 1，将该标点符号纳入当前片段。
   - **最终输出**：根据修正后的字符范围切片原始文本，生成最终的文本列表和概率列表。

# Anti-Patterns
- **配置与初始化**：
  - 不要硬编码 Tokenizer 路径，必须使用配置中的参数。
  - 不要删除原有的字符级分割功能，必须保持兼容性。
- **预处理相关**：
  - 不要在过滤之前添加EOS，避免对无效数据进行操作。
  - 不要直接从结果列表中删除被过滤的样本，必须用空列表 `[]` 占位以保持索引对齐。
- **分割相关（性能与逻辑）**：
  - 禁止在循环内部调用 `tokenizer(text)`。
  - 禁止在分割阶段使用固定的概率阈值进行初次筛选（应使用优先队列排序）。
  - 禁止使用 `fallback_separators`（如句号、空格等）进行强制分割。
  - 禁止使用复杂的并查集或区间合并算法，必须严格按照“从后往前贪心”逻辑实现合并阶段。
  - **禁止在候选点生成或排序时使用 Python 循环**，必须使用 Numpy 向量化操作。
  - **禁止在分割循环中使用线性搜索**查找片段，必须使用二分查找。
  - **禁止使用 Token 的首字符**获取分割概率，必须使用末尾字符（`end_chars - 1`）。
  - 禁止忽略 `min_unique_chars` 的过滤逻辑。
- **结果构建相关**：
  - 不要将标点符号孤立地分配给下一句的开头。
  - 不要忽略Token offset mapping中的字符边界信息（在Token模式下）。

## Triggers

- 批量分句添加eos
- max_strategy 策略选择
- numpy向量化加速
- 二分查找优化分割
- 基于概率的贪心切分
- 反向贪心合并
- 修复分句标点归属
