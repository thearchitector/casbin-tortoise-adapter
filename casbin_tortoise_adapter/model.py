from __future__ import annotations

from typing import TYPE_CHECKING

from tortoise.fields import CharField, IntField
from tortoise.models import Model

if TYPE_CHECKING:
    from tortoise.fields import Field


class CasbinRule(Model):
    id: Field[int] = IntField(pk=True)
    ptype: Field[str] = CharField(max_length=255)
    v0: Field[str] = CharField(max_length=255, null=True)
    v1: Field[str] = CharField(max_length=255, null=True)
    v2: Field[str] = CharField(max_length=255, null=True)
    v3: Field[str] = CharField(max_length=255, null=True)
    v4: Field[str] = CharField(max_length=255, null=True)
    v5: Field[str] = CharField(max_length=255, null=True)

    class Meta(Model.Meta):
        table: str = "casbin_rule"

    def __str__(self) -> str:
        arr = [self.ptype]
        for v in (self.v0, self.v1, self.v2, self.v3, self.v4, self.v5):
            if not v:
                break
            arr.append(v)

        return ", ".join(arr)

    def __repr__(self) -> str:
        return '<CasbinRule {}: "{}">'.format(self.id, str(self))
