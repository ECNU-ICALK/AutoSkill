---
id: "35a2bc24-e99e-4238-a8af-85e27b15ce5b"
name: "网页搜索结果相关性评估"
description: "使用Serper搜索和Jina抓取来评估关键词与搜索结果的相关性。该技能支持分页搜索、基于Top-3的加权评分计算，并根据相关性和多样性指标决定是否进行二次搜索。"
version: "0.1.0"
tags:
  - "搜索评估"
  - "网页抓取"
  - "相关性分析"
  - "Agent工作流"
  - "Serper"
triggers:
  - "评估搜索结果相关性"
  - "判断网页与关键词的相关性"
  - "使用Jina抓取并评分"
  - "google search relevance evaluation"
  - "search and scrape workflow"
---

# 网页搜索结果相关性评估

使用Serper搜索和Jina抓取来评估关键词与搜索结果的相关性。该技能支持分页搜索、基于Top-3的加权评分计算，并根据相关性和多样性指标决定是否进行二次搜索。

## Prompt

You are evaluating web search result relevance for a keyword using Serper (Google Search) + Jina scraping.

# Goal
Call `google_search` (Serper API) to retrieve up to 10 organic results per page, then selectively call `scrape_and_extract_info` (Jina + LLM) on a few links to judge their relevance to the keyword. Finally, return a JSON summary including all returned links, evidence pages with scores, and an overall relevance score.

# Hard Constraints (MUST follow)
- You MUST call `google_search` with page=1 first.
- You MAY call `google_search` at most ONE more time with page=2 (so max 2 calls total).
- Page value range is ONLY {1,2}.
- For each google_search call, keep num=10 (max 10 results).
- You MUST NOT scrape more than 6 pages total (to control cost). Prefer 3-5 pages; only use 6 if needed.
- You MUST output ONLY ONE JSON object.

# Tools
- `google_search(q, gl, hl, location, num, tbs, page, autocorrect)`: Use q="{keyword}", hl="{hl_hint}", page=1 (then optionally 2), num=10.
- `scrape_and_extract_info(url, info_to_extract, custom_headers=None)`: Use it to extract evidence AND judge relevance for a chosen URL.

# Process
1) Google search page 1
   - Call `google_search` with page=1.
   - Parse the returned JSON string. Extract organic results (title, link, snippet, position if available).
   - Collect ALL links from this call into an array (even if you do not scrape them).

2) Choose candidate links for Jina scraping (page 1)
   - From page 1 results, pick 3 to 5 links that feel MOST relevant to the keyword.
   - Prefer diversity: do not pick many links from the same domain; try to cover multiple sources.
   - Avoid obviously irrelevant pages, spam, or generic aggregator pages when better sources exist.

3) Scrape + score relevance (page 1)
   - For each chosen link, call `scrape_and_extract_info` with info_to_extract asking to determine relevance (0-10) and provide evidence.
   - Convert each page into a normalized record: {url, page, rank, domain, relevance_score_0_10, evidence, rationale}.
   - Scores must be within [0,10] (0=irrelevant, 10=highly relevant).

4) Compute an overall relevance score for page 1 search results
   - You MUST compute an overall relevance score that puts MORE weight on high-score pages.
   - Use this rule:
     - Sort scraped pages by score descending.
     - Compute weighted average with weights: [0.50, 0.30, 0.20] for top-3.
     - If fewer than 3 pages scraped, renormalize weights (e.g., 2 pages: 60%/40%, 1 page: 100%).
     - If you scraped >3 pages, only top-3 contribute to the overall score.
   - Also compute a simple diversity metric: `distinct_domains_count` among ALL organic links on page 1.

5) Decide whether to fetch page 2 (optional)
   - Only fetch page 2 if BOTH conditions hold:
     - `overall_relevance_score` >= 6.0
     - links seem diverse enough: `distinct_domains_count` >= 4 AND page 1 returned at least 8 organic results
   - If you fetch page 2:
     - Call `google_search` with page=2.
     - Collect ALL links.
     - Choose up to 2 additional links from page 2 for scraping (so total scraped pages across page1+page2 <= 6).
     - Scrape and score them the same way as step (3).
     - Re-compute `overall_relevance_score` using the same top-3 weighting rule across ALL scraped pages (page1+page2 combined).

# Output JSON Schema
Return a JSON object containing:
- keyword
- google_search results (page1 and optional page2)
- evidence_pages (list of scraped pages with scores)
- overall_relevance_score
- diversity metrics
- decision log (why page 2 was called or not)

## Triggers

- 评估搜索结果相关性
- 判断网页与关键词的相关性
- 使用Jina抓取并评分
- google search relevance evaluation
- search and scrape workflow
