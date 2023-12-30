from __future__ import annotations

import asyncio
from dataclasses import asdict
from typing import TYPE_CHECKING

from casbin.persist import load_policy_line
from casbin.persist.adapters.asyncio import (
    AsyncAdapter,
    AsyncBatchAdapter,
    AsyncFilteredAdapter,
    AsyncUpdateAdapter,
)
from tortoise.expressions import Q

from .model import CasbinRule

if TYPE_CHECKING:
    from typing import Dict, List, Tuple, Type

    from casbin.model import Model

    from .filter import RuleFilter
    from .typing import RuleType

    class Assertion:
        policy: List[RuleType]


class TortoiseAdapter(
    AsyncBatchAdapter, AsyncUpdateAdapter, AsyncFilteredAdapter, AsyncAdapter
):
    """An async Casbin adapter for Tortoise ORM."""

    def __init__(self, modelclass: Type[CasbinRule] = CasbinRule) -> None:
        if not issubclass(modelclass, CasbinRule):
            raise TypeError(
                "The provided model class must be a subclass of CasbinRule!"
            )

        self.modelclass: Type[CasbinRule] = modelclass
        self._filtered: bool = False

    async def load_policy(self, model: Model) -> None:
        """Loads all policy rules from storage."""
        for line in await self.modelclass.all():
            load_policy_line(str(line), model)

    async def load_filtered_policy(self, model: Model, filter: RuleFilter) -> None:
        """Loads all policy rules that match the filter from storage."""
        rules = await self.modelclass.filter(
            **{f"{f}__in": v for f, v in asdict(filter).items() if v}
        )

        for line in rules:
            load_policy_line(str(line), model)

        self._filtered = True

    async def save_policy(self, model: Model) -> None:
        """Saves all policy rules to storage."""
        raw: Dict[str, Dict[str, Assertion]] = model.model
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
    ) -> bool:
        """Saves a policy rule to storage."""
        await self._to_rule(ptype, rule).save()
        return True

    async def add_policies(  # pyright: ignore
        self, sec: str, ptype: str, rules: List[RuleType]
    ) -> bool:
        """Saves policy rules to storage."""
        batch = [self._to_rule(ptype, rule) for rule in rules]
        rs: List[CasbinRule] = await self.modelclass.bulk_create(batch)  # type: ignore
        return len(rs) > 0

    async def update_policy(  # pyright: ignore
        self, sec: str, ptype: str, old_rule: RuleType, new_policy: RuleType
    ) -> bool:
        """
        Updates a policy rule from storage. This is part of the Auto-Save feature.
        """
        vs = {f"v{i}": rule for i, rule in enumerate(old_rule)}
        r = await self.modelclass.filter(ptype=ptype, **vs).update(
            **{
                f"v{i}": (new_policy[i] if i < len(new_policy) else None)
                for i in range(6)
            }
        )
        return r > 0

    async def update_policies(  # pyright: ignore
        self,
        sec: str,
        ptype: str,
        old_rules: List[RuleType],
        new_rules: List[RuleType],
    ) -> bool:
        """Updates the old rules with the new rules."""
        if not old_rules or not new_rules or (len(old_rules) != len(new_rules)):
            raise ValueError(
                "There must be at least one mapped pair of old and new rules."
            )

        rs = await asyncio.gather(
            *[
                self.update_policy(sec, ptype, old_rule, new_rule)
                for old_rule, new_rule in zip(old_rules, new_rules)
            ]
        )
        return all(rs)

    async def update_filtered_policies(  # pyright: ignore
        self,
        sec: str,
        ptype: str,
        new_rules: List[RuleType],
        field_index: int,
        *field_values: Tuple[str],
    ) -> List[RuleType]:
        """Updates the old filtered rules with the new rules."""
        if not (0 <= field_index <= 5) or not (
            1 <= field_index + len(field_values) <= 6
        ):
            return []

        vs = {f"v{field_index + i}": v for i, v in enumerate(field_values) if v}
        rs = await self.modelclass.filter(**vs).all()
        old_rules = [self._from_rule(r) for r in rs]

        await self.update_policies(sec, ptype, old_rules, new_rules)

        return old_rules

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

        vs = {f"v{field_index + i}": v for i, v in enumerate(field_values) if v}
        r = await self.modelclass.filter(**vs).delete()
        return r > 0

    async def remove_policies(  # pyright: ignore
        self, sec: str, ptype: str, rules: List[RuleType]
    ) -> bool:
        """Removes policy rules from storage."""
        if not rules:
            return False

        qs = [Q(**{f"v{i}": v for i, v in enumerate(rule)}) for rule in rules]
        r = await self.modelclass.filter(Q(*qs, join_type=Q.OR), ptype=ptype).delete()
        return r > 0

    def is_filtered(self) -> bool:  # pyright: ignore
        """Returns if the loaded policy is filtered or not."""
        return self._filtered

    def _to_rule(self, ptype: str, rule: RuleType) -> CasbinRule:
        kwargs: Dict[str, str] = {f"v{i}": v for i, v in enumerate(rule)}
        return self.modelclass(ptype=ptype, **kwargs)

    def _from_rule(self, rule: CasbinRule) -> RuleType:
        return str(rule).split(", ")[1:]
