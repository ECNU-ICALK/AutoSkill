#!/usr/bin/env python3
"""
AutoSkill-Agent entrypoint.

This script keeps only CLI bootstrapping. Core modules are split into independent files:
- engine/
"""

from __future__ import annotations

from engine.cli import main


if __name__ == "__main__":
    main()
