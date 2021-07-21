from tortoise import fields
from tortoise.models import Model


class CasbinRule(Model):
    id: fields.IntField = fields.IntField(pk=True)
    ptype: fields.CharField = fields.CharField(max_length=255)
    v0: fields.CharField = fields.CharField(max_length=255, null=True)
    v1: fields.CharField = fields.CharField(max_length=255, null=True)
    v2: fields.CharField = fields.CharField(max_length=255, null=True)
    v3: fields.CharField = fields.CharField(max_length=255, null=True)
    v4: fields.CharField = fields.CharField(max_length=255, null=True)
    v5: fields.CharField = fields.CharField(max_length=255, null=True)

    class Meta:
        table: str = "casbin_rule"

    def __str__(self):
        arr = [self.ptype]
        for v in (self.v0, self.v1, self.v2, self.v3, self.v4, self.v5):
            if v is None:
                break
            arr.append(v)

        return ", ".join(arr)

    def __repr__(self):
        return '<CasbinRule {}: "{}">'.format(self.id, str(self))
