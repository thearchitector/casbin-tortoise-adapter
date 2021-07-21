from dataclasses import dataclass, field
from typing import List


@dataclass
class RuleFilter:
    ptype: List = field(default_factory=list)
    v0: List = field(default_factory=list)
    v1: List = field(default_factory=list)
    v2: List = field(default_factory=list)
    v3: List = field(default_factory=list)
    v4: List = field(default_factory=list)
    v5: List = field(default_factory=list)
