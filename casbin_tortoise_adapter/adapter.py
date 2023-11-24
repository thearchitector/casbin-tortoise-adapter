from __future__ import annotations

import asyncio
from dataclasses import asdict
from typing import TYPE_CHECKING

from casbin.persist import (
    Adapter,
    BatchAdapter,
    FilteredAdapter,
    load_policy_line,  # pyright: ignore
)
from casbin.persist.adapters.update_adapter import UpdateAdapter
from tortoise.expressions import Q

from .model import CasbinRule

if TYPE_CHECKING:
    from typing import Dict, List, Tuple, Type

    from casbin.model import Model

    from .filter import RuleFilter
    from .typing import RuleType

    class Assertion:
        policy: List[RuleType]


class TortoiseAdapter(BatchAdapter, UpdateAdapter, FilteredAdapter, Adapter):
    """An async Casbin adapter for Tortoise ORM."""

    def __init__(self, modelclass: Type[CasbinRule] = CasbinRule) -> None:
        if not issubclass(modelclass, CasbinRule):  # pyright: ignore
            raise TypeError(
                "The provided model class must be a subclass of CasbinRule!"
            )

        self.modelclass: Type[CasbinRule] = modelclass
        self._filtered: bool = False

    async def load_policy(self, model: Model) -> None:
        """Loads all policy rules from storage."""
        for line in await self.modelclass.all():
            load_policy_line(str(line), model)

    async def load_filtered_policy(  # pyright: ignore
        self, model: Model, filter: RuleFilter
    ) -> None:
        """Loads all policy rules that match the filter from storage."""
        rules = await self.modelclass.filter(
            **{f"{f}__in": v for f, v in asdict(filter).items() if v}
        )

        for line in rules:
            load_policy_line(str(line), model)

        self._filtered = True

    async def save_policy(self, model: Model) -> None:  # pyright: ignore
        """Saves all policy rules to storage."""
        raw: Dict[str, Dict[str, Assertion]] = model.model  # pyright: ignore
        rules: List[CasbinRule] = [
            self._to_rule(ptype, rule)
            for sec in ("p", "g")
            for ptype, ast in raw.get(sec, {}).items()
            for rule in ast.policy
        ]
        await self.modelclass.all().delete()
        await self.modelclass.bulk_create(rules)

    async def add_policy(  # pyright: ignore
        self, sec: str, ptype: str, rule: RuleType
    ) -> None:
        """Saves a policy rule to storage."""
        await self._to_rule(ptype, rule).save()

    async def add_policies(  # pyright: ignore
        self, sec: str, ptype: str, rules: List[RuleType]
    ) -> None:
        """Saves policy rules to storage."""
        batch = [self._to_rule(ptype, rule) for rule in rules]
        await self.modelclass.bulk_create(batch)

    async def update_policy(  # pyright: ignore
        self, sec: str, ptype: str, old_rule: RuleType, new_policy: RuleType
    ) -> None:
        """
        Updates a policy rule from storage. This is part of the Auto-Save feature.
        """
        vs = {f"v{i}": rule for i, rule in enumerate(old_rule)}
        r = self.modelclass.filter(ptype=ptype, **vs)
        await r.update(
            **{
                f"v{i}": (new_policy[i] if i < len(new_policy) else None)
                for i in range(6)
            }
        )

    async def update_policies(
        self,
        sec: str,
        ptype: str,
        old_rules: List[RuleType],
        new_rules: List[RuleType],
    ) -> None:
        """Updates the old rules with the new rules."""
        await asyncio.gather(
            *[
                self.update_policy(sec, ptype, old_rule, new_rule)
                for old_rule, new_rule in zip(old_rules, new_rules)
            ]
        )

    async def remove_policy(  # pyright: ignore
        self, sec: str, ptype: str, rule: RuleType
    ) -> bool:
        """Removes a policy rule from storage."""
        vs = {f"v{i}": v for i, v in enumerate(rule)}
        r = await self.modelclass.filter(ptype=ptype, **vs).delete()
        return r > 0

    async def remove_filtered_policy(  # pyright: ignore
        self, sec: str, ptype: str, field_index: int, *field_values: Tuple[str]
    ) -> bool:
        """
        Removes policy rules that match the filter from the storage. This is part
        of the Auto-Save feature.
        """
        if not (0 <= field_index <= 5) or not (
            1 <= field_index + len(field_values) <= 6
        ):
            return False

        r = 0
        vs = {f"v{field_index + i}": v for i, v in enumerate(field_values) if v}
        if vs:
            r = await self.modelclass.filter(**vs).delete()

        return r > 0

    async def remove_policies(  # pyright: ignore
        self, sec: str, ptype: str, rules: List[RuleType]
    ) -> None:
        """Removes policy rules from storage."""
        if not rules:
            return

        qs = [Q(**{f"v{i}": v for i, v in enumerate(rule)}) for rule in rules]
        await self.modelclass.filter(Q(*qs, join_type=Q.OR), ptype=ptype).delete()

    def is_filtered(self) -> bool:
        """Returns if the loaded policy is filtered or not."""
        return self._filtered

    def _to_rule(self, ptype: str, rule: RuleType) -> CasbinRule:
        kwargs: Dict[str, str] = {f"v{i}": v for i, v in enumerate(rule)}
        return self.modelclass(ptype=ptype, **kwargs)
