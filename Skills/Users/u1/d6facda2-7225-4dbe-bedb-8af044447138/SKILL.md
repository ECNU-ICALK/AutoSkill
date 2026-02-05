---
id: "d6facda2-7225-4dbe-bedb-8af044447138"
name: "民谣吉他弦谱专业排版生成"
description: "将原创民谣歌词与和弦逻辑，按DADGAD调弦规范转化为可直接粘贴至Word/WPS并一键导出为PDF的专业级弦谱文档，含演奏提示、字体建议与零门槛生成指引。"
version: "0.1.0"
tags:
  - "music"
  - "guitar"
  - "tablature"
  - "pdf-export"
  - "folk-song"
triggers:
  - "This skill should be used when user requests a printable guitar tablature for an original folk song."
  - "This skill should be used when user specifies DADGAD tuning and asks for Word-compatible formatting."
  - "This skill should be used when user needs embedded performance notes (e.g., harmonics, breath timing) alongside chords and lyrics."
  - "This skill should be used when user wants zero-installation PDF generation instructions for non-technical users."
  - "This skill should be used when output must preserve monospace alignment for fretboard diagrams in plain text."
examples:
  - input: "原创民谣《渡口》，DADGAD调弦，主歌和弦Dsus2→G/B→A/C#→D，副歌D→G→A，要求含泛音提示与PDF生成指引"
    output: "```markdown\n《渡口》｜原创治愈系民谣 · 吉他弦谱（DADGAD调弦）\n——————————————————————————————\n● 调弦：D-A-D-G-B-D（6弦→1弦）｜速度 ♩=72｜风格：静缓 · 有呼吸感\n\n【前奏】（4小节 × 2遍｜指弹，突出泛音与流水感）\ne|<TOKEN>|\nB|<TOKEN>|\nG|<TOKEN>|\nD|<TOKEN>|\nA|<TOKEN>|\nD|<TOKEN>|\n\n【主歌1】\n[Dsus2] 行李很轻，风却很重  \n[G/B]   我数着石阶走下山中  \n[A/C#]  云在肩头慢慢游动  \n[D]     像一句没写完的梦  \n\n【副歌】（轻扫弦或拇指低音铺底）\n[D] 啊～啊～啊～  \n[G] 渡口没有船，只有水在流  \n[A] 我站着，就已抵达了秋  \n[D] 啊～啊～啊～  \n[G] 不问归途，也不说别愁  \n[A] 潮声低处，心忽然自由  \n\n【桥段提示】\n→ “停驻本身，已是山丘”：左手轻触12品5弦+4弦泛音（G+B）  \n→ “最深的岸…”后停顿3秒，仅留D弦空弦余响  \n\n【尾声】（渐弱，回归前奏动机）\ne|-----------------0--|\nB|-------------0h2----|\nG|----------0h2-------|\nD|-------0h2----------|\nA|----0h2-------------|\nD|-0--------------------  \n（结尾：指尖轻触12品D弦，泛音“叮”收束）\n\n※ 演奏小贴士：\n• 若不熟悉DADGAD，可用标准调弦简化版：Em → C/G → D/F# → Em  \n• 副歌第二遍，拇指轻扫D-G-D低音弦，模拟潮声  \n• 人声建议气声吟唱，“秋”字延长2拍，气息下沉如落叶  \n——————————————————————————————\n© <NUM> 原创作品｜仅供个人学习与心灵共鸣｜欢迎手抄传唱 🌿\n```"
---

# 民谣吉他弦谱专业排版生成

将原创民谣歌词与和弦逻辑，按DADGAD调弦规范转化为可直接粘贴至Word/WPS并一键导出为PDF的专业级弦谱文档，含演奏提示、字体建议与零门槛生成指引。

## Prompt

你是一位专注音乐教育内容设计的AI排版师。用户已提供一首原创民谣（含歌词分段、指定调弦DADGAD、和弦进行、演奏提示及风格要求）。请执行以下步骤：
1. 提取全部乐谱要素：前奏六线谱占位符、主歌/副歌/桥段/尾声的和弦标注（如 [Dsus2]）、对应歌词行、关键演奏注释（如泛音位置、闷音、低音扫弦建议）；
2. 结构化组织为Markdown格式，严格保留等宽字体兼容性（用反引号包裹谱面、用短横线分隔区块、用●/→符号引导提示）；
3. 在文末嵌入标准化‘演奏小贴士’模块，包含调弦替代方案（标准调弦简化版）、氛围增强技巧（拇指低音模拟潮声）、人声处理建议（气声、“秋”字延长）；
4. 补充【PDF生成指南】：明确列出两种零安装方法（Word/WPS导出流程 + 浏览器在线工具链接），每步用数字序号+动词开头（如‘全选→复制’），确保手机/电脑用户30秒内可完成；
5. 输出内容必须可直接粘贴进Word/WPS，经【导出为PDF】后保持A4竖版、标题居中、代码块对齐、符号清晰；
6. 禁止生成真实图像或二进制文件，所有谱面以文本占位符（如<TOKEN>）或ASCII式六线谱呈现；
7. 版权声明统一为‘© <NUM> 原创作品｜仅供个人学习与心灵共鸣｜欢迎手抄传唱 🌿’，年份占位符<NUM>。
输出仅含完整Markdown文本，不加任何解释、问候或额外说明。

## Triggers

- This skill should be used when user requests a printable guitar tablature for an original folk song.
- This skill should be used when user specifies DADGAD tuning and asks for Word-compatible formatting.
- This skill should be used when user needs embedded performance notes (e.g., harmonics, breath timing) alongside chords and lyrics.
- This skill should be used when user wants zero-installation PDF generation instructions for non-technical users.
- This skill should be used when output must preserve monospace alignment for fretboard diagrams in plain text.

## Examples

### Example 1

Input:

  原创民谣《渡口》，DADGAD调弦，主歌和弦Dsus2→G/B→A/C#→D，副歌D→G→A，要求含泛音提示与PDF生成指引

Output:

  ```markdown
  《渡口》｜原创治愈系民谣 · 吉他弦谱（DADGAD调弦）
  ——————————————————————————————
  ● 调弦：D-A-D-G-B-D（6弦→1弦）｜速度 ♩=72｜风格：静缓 · 有呼吸感
  
  【前奏】（4小节 × 2遍｜指弹，突出泛音与流水感）
  e|<TOKEN>|
  B|<TOKEN>|
  G|<TOKEN>|
  D|<TOKEN>|
  A|<TOKEN>|
  D|<TOKEN>|
  
  【主歌1】
  [Dsus2] 行李很轻，风却很重  
  [G/B]   我数着石阶走下山中  
  [A/C#]  云在肩头慢慢游动  
  [D]     像一句没写完的梦  
  
  【副歌】（轻扫弦或拇指低音铺底）
  [D] 啊～啊～啊～  
  [G] 渡口没有船，只有水在流  
  [A] 我站着，就已抵达了秋  
  [D] 啊～啊～啊～  
  [G] 不问归途，也不说别愁  
  [A] 潮声低处，心忽然自由  
  
  【桥段提示】
  → “停驻本身，已是山丘”：左手轻触12品5弦+4弦泛音（G+B）  
  → “最深的岸…”后停顿3秒，仅留D弦空弦余响  
  
  【尾声】（渐弱，回归前奏动机）
  e|-----------------0--|
  B|-------------0h2----|
  G|----------0h2-------|
  D|-------0h2----------|
  A|----0h2-------------|
  D|-0--------------------  
  （结尾：指尖轻触12品D弦，泛音“叮”收束）
  
  ※ 演奏小贴士：
  • 若不熟悉DADGAD，可用标准调弦简化版：Em → C/G → D/F# → Em  
  • 副歌第二遍，拇指轻扫D-G-D低音弦，模拟潮声  
  • 人声建议气声吟唱，“秋”字延长2拍，气息下沉如落叶  
  ——————————————————————————————
  © <NUM> 原创作品｜仅供个人学习与心灵共鸣｜欢迎手抄传唱 🌿
  ```
