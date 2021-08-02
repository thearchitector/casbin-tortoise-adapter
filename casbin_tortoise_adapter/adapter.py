from dataclasses import asdict
from typing import List, Tuple

from casbin.model import Model
from casbin.persist import Adapter, load_policy_line
from tortoise.query_utils import Q

from .filter import RuleFilter
from .model import CasbinRule
from .typing import RuleType


class TortoiseAdapter(Adapter):
    """An async Casbin adapter for Tortoise ORM."""

    def __init__(self, modelclass=CasbinRule):
        if not issubclass(modelclass, CasbinRule):
            raise TypeError(
                "The provided model class must be a subclass of CasbinRule!"
            )

        self.modelclass = modelclass
        self._filtered = False

    async def load_policy(self, model: Model):
        """Loads all policy rules from storage."""
        for line in await self.modelclass.all():
            load_policy_line(str(line), model)

    async def load_filtered_policy(self, model: Model, filter: RuleFilter):
        """Loads all policy rules that match the filter from storage."""
        rules = await self.modelclass.filter(
            **{f"{f}__in": v for f, v in asdict(filter).items() if v}
        ).all()

        for line in rules:
            load_policy_line(str(line), model)

        self._filtered = True

    async def save_policy(self, model: Model):
        """Saves all policy rules to storage."""
        rules = [
            self._to_rule(ptype, rule)
            for sec in ["p", "g"]
            for ptype, ast in model.model.get(sec, {}).items()
            for rule in ast.policy
        ]
        await self.modelclass.all().delete()
        await self.modelclass.bulk_create(rules)

    async def add_policy(self, sec: str, ptype: str, rule: RuleType):
        """Saves a policy rule to storage."""
        await self._to_rule(ptype, rule).save()

    async def add_policies(self, sec: str, ptype: str, rules: List[RuleType]):
        """Saves policy rules to storage."""
        batch = [self._to_rule(ptype, rule) for rule in rules]
        await self.modelclass.bulk_create(batch)

    async def remove_policy(self, sec: str, ptype: str, rule: RuleType):
        """Removes a policy rule from storage."""
        vs = {f"v{i}": rule[i] if len(rule) > i else None for i in range(6)}
        r = await self.modelclass.filter(ptype=ptype, **vs).delete()
        return r > 0

    async def remove_policies(self, sec, ptype, rules: List[RuleType]):
        """Removes policy rules from storage."""
        if not rules:
            return

        qs = [
            Q(**{f"v{i}": rule[i] if len(rule) > i else None for i in range(6)})
            for i, rule in enumerate(rules)
        ]
        await self.modelclass.filter(Q(*qs, join_type=Q.OR), ptype=ptype).delete()

    async def remove_filtered_policy(
        self, sec: str, ptype: str, field_index: int, *field_values: Tuple[str]
    ):
        """Removes policy rules that match the filter from the storage. This is part
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

    def is_filtered(self):
        return self._filtered

    def _to_rule(self, ptype: str, rule: RuleType):
        kwargs = {f"v{i}": v for i, v in enumerate(rule)}
        return self.modelclass(ptype=ptype, **kwargs)
