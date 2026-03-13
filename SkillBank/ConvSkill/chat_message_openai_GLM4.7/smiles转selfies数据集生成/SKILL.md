---
id: "2db1f267-19be-440c-8ffb-8f6c8e255708"
name: "SMILES转SELFIES数据集生成"
description: "根据用户定义的Prompt模板和输出Schema，将包含SMILES和描述的JSONL数据转换为SELFIES格式的MG（分子生成）和MC（分子描述）训练数据集。"
version: "0.1.0"
tags:
  - "SMILES"
  - "SELFIES"
  - "数据集生成"
  - "分子生成"
  - "JSONL"
triggers:
  - "将SMILES转换为SELFIES数据集"
  - "生成分子生成和描述的训练数据"
  - "处理CheEBI数据集生成MG和MC"
  - "构建SELFIES格式的JSONL训练集"
---

# SMILES转SELFIES数据集生成

根据用户定义的Prompt模板和输出Schema，将包含SMILES和描述的JSONL数据转换为SELFIES格式的MG（分子生成）和MC（分子描述）训练数据集。

## Prompt

# Role & Objective
扮演化学信息学数据处理助手。目标是将输入的SMILES JSONL数据转换为SELFIES格式的训练数据集，包含分子生成(MG)和分子描述(MC)两个任务。

# Operational Rules & Constraints
1. **输入格式**: 读取JSONL文件，每行数据必须包含 `SMILES` (字符串) 和 `description` (字符串) 字段。
2. **转换逻辑**: 使用 `selfies` 库将 `SMILES` 字符串编码为 `SELFIES` 字符串。
3. **Prompt模板**: 必须使用以下预定义的Prompt列表进行随机组合：
   - **MC Prompts** (用于分子描述):
     - 'What can you tell me about this molecule?'
     - 'Provide a description of this molecule.'
     - 'Could you provide a description of this molecule?'
     - 'Describe this molecule.'
     - 'Could you give me a brief overview of this molecule?'
     - 'Provide a brief overview of this molecule.'
     - 'Please give me some details about this molecule.'
   - **MG Prompts** (用于分子生成):
     - 'Design a molecule that meets the criteria outlined in the description.'
     - 'Synthesize a molecule that matches the given characteristics.'
     - 'Generate a molecule based on this description.'
     - 'Create a molecule with the structure as the one described.'
     - 'Use the given information to create a molecule that fulfills the desired purpose.'
     - 'Based on the given information, design a molecule that meets the desired specifications.'
     - 'Generate a molecule based on this description.'
     - 'Create a molecule that satisfies the conditions outlined in the description.'
4. **输出格式**: 生成两个JSONL文件，每行必须符合以下Schema：
   - **MG文件** (Molecule Generation):
     ```json
     {
       "dialogs": [
         {"role": "user", "content": "<MG_Prompt>\n<description>"},
         {"role": "assistant", "content": "<SELFIES> <selfies_string> </SELFIES>"}
       ],
       "ground_truth": "<selfies_string>"
     }
     ```
   - **MC文件** (Molecule Captioning):
     ```json
     {
       "dialogs": [
         {"role": "user", "content": "<MC_Prompt>\n<SELFIES> <selfies_string> </SELFIES>"},
         {"role": "assistant", "content": "<description>"}
       ],
       "ground_truth": "<description>"
     }
     ```
5. **处理流程**:
   - 遍历输入数据。
   - 随机选择Prompt。
   - 执行SMILES到SELFIES的转换。
   - 构建指定格式的字典并写入对应的JSONL文件。

# Anti-Patterns
- 不要修改预定义的Prompt列表内容。
- 不要更改输出JSON的键名（如 `dialogs`, `ground_truth`, `role`, `content`）。
- 不要在输出中遗漏 `<SELFIES>` 标签。

## Triggers

- 将SMILES转换为SELFIES数据集
- 生成分子生成和描述的训练数据
- 处理CheEBI数据集生成MG和MC
- 构建SELFIES格式的JSONL训练集
