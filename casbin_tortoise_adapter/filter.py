from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List


@dataclass
class RuleFilter:
    ptype: List[str] = field(default_factory=list)
    v0: List[str] = field(default_factory=list)
    v1: List[str] = field(default_factory=list)
    v2: List[str] = field(default_factory=list)
    v3: List[str] = field(default_factory=list)
    v4: List[str] = field(default_factory=list)
    v5: List[str] = field(default_factory=list)
