from __future__ import annotations
from dataclasses import dataclass
from regex import Pattern


@dataclass
class SkipRule:
    rule_name: str
    source: str


@dataclass
class SegmenterConfig:
    skip: SkipRule | None
    break_rules: set[str]
    pattern: Pattern
    debug_pattern: Pattern
    break_candidates_pattern: Pattern | None
