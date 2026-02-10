---
id: "c9dbd0f0-a786-4d9f-ac29-9a2ef87d3563"
name: "high-performance-log-parser-in-c"
description: "A reusable capability to implement memory-efficient, streaming log parsers in C for large files, avoiding Python and prioritizing concise, practical comments."
version: "0.1.1"
tags:
  - "c"
  - "log-parsing"
  - "mmap"
  - "streaming"
  - "regex"
  - "performance"
triggers:
  - "implement log parser in C"
  - "high-performance log parsing without Python"
  - "memory-efficient log parser in C"
  - "streaming log parser with mmap in C"
  - "concise-comment C log parser"
---

# high-performance-log-parser-in-c

A reusable capability to implement memory-efficient, streaming log parsers in C for large files, avoiding Python and prioritizing concise, practical comments.

## Prompt

# Goal
Implement a high-performance log parser in C for large log files, using memory-mapped I/O and line-by-line streaming, with no dependency on Python or interpreted runtimes.

# Constraints & Style
- Language: C only (no C++, no Python bindings, no external scripting layers)
- Memory efficiency: use `mmap()` for zero-copy file access; avoid loading entire file into RAM
- Streaming: expose parsing as an iterator-like interface (e.g., callback-driven or stateful `next_line()`/`next_entry()`)
- Regex: use POSIX `regcomp()`/`regexec()` (not PCRE unless explicitly required); pre-compile patterns once
- Error handling: recover per-line (skip malformed lines), log errors minimally (e.g., via `errno` or simple codes), no exceptions
- Comments: concise and practical — explain *why* (e.g., "// mmap avoids heap allocation for 10GB files") or *what hazard is avoided* (e.g., "// Avoids strlen() on mmap'd region"); skip boilerplate and line-by-line 'what' comments
- No dynamic allocations per line: prefer stack buffers or reusable pools; all strings in output structs (e.g., `log_entry_t`) must be `const char*` pointing into the mmap'd buffer — no `strdup`, no dynamic string copies
- Reuse a single fixed-size working buffer (`buf`) for null-terminating lines; reallocate only when necessary
- Encoding: assume UTF-8 or ASCII; no transcoding — reject or pass through invalid byte sequences
- Output: structured C structs (e.g., `typedef struct { const char *timestamp; const char *level; const char *message; size_t raw_offset; } log_entry_t`) — no JSON serialization built-in unless requested
- Emit only the parser implementation: omit `main()`, `#include` guards, build instructions, compile notes, or usage boilerplate
- Annotate *only* functions critical to correctness, performance, or interface contract (e.g., `log_parser_init`, `log_parser_parse_line`, `log_parser_next`, `log_parser_destroy`)
- Omit error-checking verbosity in comments; assume caller handles `errno`/return codes

## Triggers

- implement log parser in C
- high-performance log parsing without Python
- memory-efficient log parser in C
- streaming log parser with mmap in C
- concise-comment C log parser
