---
id: "eb26e8f8-0507-4e5d-a905-a92e45abf519"
name: "Standard release process"
description: "General SOP for common requests related to self, current, if."
version: "0.1.0"
tags:
  - "self"
  - "current"
  - "if"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# Standard release process

General SOP for common requests related to self, current, if.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) 1. 手上有头寸而采取观望，导致资产大幅缩水的，应该惩罚，比如最大不利波动是最大有利波动的1.5倍以上时，按照比值进行惩罚
2) 2. 手上有现金购买25只以上的股票时，没有购买导致错过了资产的增长，比如最大有利波动是最大不利波动的1.5倍以上时，按照比值进行惩罚
3) 3. 默认的奖励依然是 min(abs(future_max - current), abs(current - future_min)) / max(abs(future_max - current), abs(current - future_min
4) if action == 0:  # 观望
5) 如果我们由于资金或头寸不足而观望，那么应该给予奖励
6) current_buying_power = self._cash_in_hand / current
7) if transacted_shares == 0 and (current_buying_power < 25 or self._num_stocks_owned < 25
8) 确保不会除以零
9) buying_power_reward = 1 / current_buying_power if current_buying_power >= 1 else 1
10) stock_owned_reward = 1 / self._num_stocks_owned if self._num_stocks_owned >= 1 else 1

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
