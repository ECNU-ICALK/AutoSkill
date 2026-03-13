---
id: "7c8ed08a-2ade-433d-87b2-9ba1723598f2"
name: "ترجمه انگلیسی به فارسی بدون توضیح اضافه"
description: "این مهارت برای ترجمه متن‌های انگلیسی به زبان فارسی استفاده می‌شود و باید بدون ارائه هیچگونه توضیح اضافه، متن یا مقدمه‌ای انجام شود."
version: "0.1.1"
tags:
  - "ترجمه"
  - "فارسی"
  - "انگلیسی"
  - "بدون توضیح"
  - "در"
  - "این"
  - "می"
triggers:
  - "متن زیر را برایم ترجمه کن به فارسی بدون توضیح اضافه لطفا"
  - "این متن را به فارسی ترجمه کن بدون توضیح"
  - "Translate to Persian without explanation"
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# ترجمه انگلیسی به فارسی بدون توضیح اضافه

این مهارت برای ترجمه متن‌های انگلیسی به زبان فارسی استفاده می‌شود و باید بدون ارائه هیچگونه توضیح اضافه، متن یا مقدمه‌ای انجام شود.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) Offline OpenAI-format conversation source.
2) Title: ae4d97e40de2e734b7877bbcda23d7f4.json#conv_1
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Primary User Questions (main evidence):
7) summarize: فصل روش شناسی جزء حیاتی هر مطالعه تحقیقی است زیرا طرح تحقیق و رویکرد اتخاذ شده برای پاسخ به سؤالات تحقیق را تشریح می کند. در این فصل روش‌های مورد استفاده در تحقیق شامل طراحی تحقیق، روش‌های جمع‌آوری داده‌ها، انتخاب نمونه، متغیرها و معیارها و تکنیک‌های تحلیلی به تفصیل ارائه می‌شود.
8) در این فصل روش شناسی مورد استفاده برای شناسایی و رتبه بندی عوامل کلیدی موفقیت یکپارچه سازی سیستم های CRM با هوش مصنوعی و سیستم مدیریت دانش ارائه می‌شود. این مطالعه، روشی کمی که وابستگی متقابل بین عوامل را در نظر می گیرد، انجام شده است.
9) فصل روش شناسی با بحث در مورد طرح تحقیق انتخاب شده برای این مطالعه و منطق پشت این انتخاب آغاز می شود. این بخش شامل بحث در مورد نقاط قوت و ضعف طرح تحقیق انتخابی و نحوه همسویی آن با سوالات و اهداف تحقیق خواهد بود.
10) در ادامه، این فصل به تشریح روش های جمع آوری داده های مورد استفاده در تحقیق می پردازد. محقق برای جمع آوری داده ها از پرسشنامه استفاده خواهد کرد. فرآیند انتخاب نمونه نیز شامل معیارهای مورد استفاده برای انتخاب نمونه‌ها تشریح خواهد شد.

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- متن زیر را برایم ترجمه کن به فارسی بدون توضیح اضافه لطفا
- این متن را به فارسی ترجمه کن بدون توضیح
- Translate to Persian without explanation
- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
