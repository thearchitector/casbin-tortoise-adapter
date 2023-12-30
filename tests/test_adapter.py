import pytest

from casbin_tortoise_adapter import CasbinRule, RuleFilter, TortoiseAdapter


def test_bad_modelclass():
    class BadModel:
        pass

    with pytest.raises(TypeError):
        TortoiseAdapter(modelclass=BadModel)


@pytest.mark.parametrize(
    "rule,string",
    (
        (
            ("p", "alice", "data1", "read"),
            "p, alice, data1, read",
        ),
        (
            ("p", "bob", "data2", "write"),
            "p, bob, data2, write",
        ),
        (
            ("p", "data2_admin", "data2", "read"),
            "p, data2_admin, data2, read",
        ),
        (
            ("p", "data2_admin", "data2", "write"),
            "p, data2_admin, data2, write",
        ),
        (
            ("g", "alice", "data2_admin", None),
            "g, alice, data2_admin",
        ),
    ),
)
def test_str(rule, string):
    ptype, v0, v1, v2 = rule
    assert str(CasbinRule(ptype=ptype, v0=v0, v1=v1, v2=v2)) == string


def test_repr():
    rule = CasbinRule(ptype="p", v0="alice", v1="data1", v2="read")
    assert repr(rule) == '<CasbinRule None: "p, alice, data1, read">'


async def test_enforcer_basic(enforcer):
    assert enforcer.enforce("alice", "data1", "read")
    assert not enforcer.enforce("alice", "data1", "write")
    assert not enforcer.enforce("bob", "data1", "read")
    assert not enforcer.enforce("bob", "data1", "write")
    assert enforcer.enforce("bob", "data2", "write")
    assert not enforcer.enforce("bob", "data2", "read")
    assert enforcer.enforce("alice", "data2", "read")
    assert enforcer.enforce("alice", "data2", "write")


async def test_add_policy(enforcer):
    assert not enforcer.enforce("eve", "data3", "read")
    res = await enforcer.add_policies(
        (("eve", "data3", "read"), ("eve", "data4", "read"))
    )
    assert res
    assert enforcer.enforce("eve", "data3", "read")
    assert enforcer.enforce("eve", "data4", "read")


async def test_add_policies(enforcer):
    assert not enforcer.enforce("dave", "data3", "read")
    res = await enforcer.add_permission_for_user("dave", "data3", "read")
    assert res
    assert enforcer.enforce("dave", "data3", "read")


async def test_save_policy(enforcer):
    assert not enforcer.enforce("alice", "data4", "read")

    model = enforcer.get_model()
    model.clear_policy()
    model.add_policy("p", "p", ["alice", "data4", "read"])
    await enforcer.get_adapter().save_policy(model)
    assert enforcer.enforce("alice", "data4", "read")


async def test_remove_policy(enforcer):
    assert not enforcer.enforce("alice", "data5", "read")
    await enforcer.add_permission_for_user("alice", "data5", "read")
    assert enforcer.enforce("alice", "data5", "read")
    await enforcer.delete_permission_for_user("alice", "data5", "read")
    assert not enforcer.enforce("alice", "data5", "read")


async def test_remove_policies(enforcer):
    assert not enforcer.enforce("alice", "data5", "read")
    assert not enforcer.enforce("alice", "data6", "read")
    await enforcer.add_policies(
        (("alice", "data5", "read"), ("alice", "data6", "read"))
    )
    assert enforcer.enforce("alice", "data5", "read")
    assert enforcer.enforce("alice", "data6", "read")
    await enforcer.remove_policies(
        (("alice", "data5", "read"), ("alice", "data6", "read"))
    )
    assert not enforcer.enforce("alice", "data5", "read")
    assert not enforcer.enforce("alice", "data6", "read")


async def test_remove_filtered_policy(enforcer):
    assert enforcer.enforce("alice", "data1", "read")
    await enforcer.remove_filtered_policy(1, "data1")
    assert not enforcer.enforce("alice", "data1", "read")

    assert enforcer.enforce("bob", "data2", "write")
    assert enforcer.enforce("alice", "data2", "read")
    assert enforcer.enforce("alice", "data2", "write")

    await enforcer.remove_filtered_policy(1, "data2", "read")

    assert enforcer.enforce("bob", "data2", "write")
    assert not enforcer.enforce("alice", "data2", "read")
    assert enforcer.enforce("alice", "data2", "write")

    await enforcer.remove_filtered_policy(2, "write")

    assert not enforcer.enforce("bob", "data2", "write")
    assert not enforcer.enforce("alice", "data2", "write")


async def test_filtered_policy(enforcer):
    filter = RuleFilter()
    filter.ptype = ["p"]
    await enforcer.load_filtered_policy(filter)
    assert enforcer.enforce("alice", "data1", "read")
    assert not enforcer.enforce("alice", "data1", "write")
    assert not enforcer.enforce("alice", "data2", "read")
    assert not enforcer.enforce("alice", "data2", "write")
    assert not enforcer.enforce("bob", "data1", "read")
    assert not enforcer.enforce("bob", "data1", "write")
    assert not enforcer.enforce("bob", "data2", "read")
    assert enforcer.enforce("bob", "data2", "write")

    filter.ptype = []
    filter.v0 = ["alice"]
    await enforcer.load_filtered_policy(filter)
    assert enforcer.enforce("alice", "data1", "read")
    assert not enforcer.enforce("alice", "data1", "write")
    assert not enforcer.enforce("alice", "data2", "read")
    assert not enforcer.enforce("alice", "data2", "write")
    assert not enforcer.enforce("bob", "data1", "read")
    assert not enforcer.enforce("bob", "data1", "write")
    assert not enforcer.enforce("bob", "data2", "read")
    assert not enforcer.enforce("bob", "data2", "write")
    assert not enforcer.enforce("data2_admin", "data2", "read")
    assert not enforcer.enforce("data2_admin", "data2", "write")

    filter.v0 = ["bob"]
    await enforcer.load_filtered_policy(filter)
    assert not enforcer.enforce("alice", "data1", "read")
    assert not enforcer.enforce("alice", "data1", "write")
    assert not enforcer.enforce("alice", "data2", "read")
    assert not enforcer.enforce("alice", "data2", "write")
    assert not enforcer.enforce("bob", "data1", "read")
    assert not enforcer.enforce("bob", "data1", "write")
    assert not enforcer.enforce("bob", "data2", "read")
    assert enforcer.enforce("bob", "data2", "write")
    assert not enforcer.enforce("data2_admin", "data2", "read")
    assert not enforcer.enforce("data2_admin", "data2", "write")

    filter.v0 = ["data2_admin"]
    await enforcer.load_filtered_policy(filter)
    assert enforcer.enforce("data2_admin", "data2", "read")
    assert enforcer.enforce("data2_admin", "data2", "read")
    assert not enforcer.enforce("alice", "data1", "read")
    assert not enforcer.enforce("alice", "data1", "write")
    assert not enforcer.enforce("alice", "data2", "read")
    assert not enforcer.enforce("alice", "data2", "write")
    assert not enforcer.enforce("bob", "data1", "read")
    assert not enforcer.enforce("bob", "data1", "write")
    assert not enforcer.enforce("bob", "data2", "read")
    assert not enforcer.enforce("bob", "data2", "write")

    filter.v0 = ["alice", "bob"]
    await enforcer.load_filtered_policy(filter)
    assert enforcer.enforce("alice", "data1", "read")
    assert not enforcer.enforce("alice", "data1", "write")
    assert not enforcer.enforce("alice", "data2", "read")
    assert not enforcer.enforce("alice", "data2", "write")
    assert not enforcer.enforce("bob", "data1", "read")
    assert not enforcer.enforce("bob", "data1", "write")
    assert not enforcer.enforce("bob", "data2", "read")
    assert enforcer.enforce("bob", "data2", "write")
    assert not enforcer.enforce("data2_admin", "data2", "read")
    assert not enforcer.enforce("data2_admin", "data2", "write")

    filter.v0 = []
    filter.v1 = ["data1"]
    await enforcer.load_filtered_policy(filter)
    assert enforcer.enforce("alice", "data1", "read")
    assert not enforcer.enforce("alice", "data1", "write")
    assert not enforcer.enforce("alice", "data2", "read")
    assert not enforcer.enforce("alice", "data2", "write")
    assert not enforcer.enforce("bob", "data1", "read")
    assert not enforcer.enforce("bob", "data1", "write")
    assert not enforcer.enforce("bob", "data2", "read")
    assert not enforcer.enforce("bob", "data2", "write")
    assert not enforcer.enforce("data2_admin", "data2", "read")
    assert not enforcer.enforce("data2_admin", "data2", "write")

    filter.v1 = ["data2"]
    await enforcer.load_filtered_policy(filter)
    assert not enforcer.enforce("alice", "data1", "read")
    assert not enforcer.enforce("alice", "data1", "write")
    assert not enforcer.enforce("alice", "data2", "read")
    assert not enforcer.enforce("alice", "data2", "write")
    assert not enforcer.enforce("bob", "data1", "read")
    assert not enforcer.enforce("bob", "data1", "write")
    assert not enforcer.enforce("bob", "data2", "read")
    assert enforcer.enforce("bob", "data2", "write")
    assert enforcer.enforce("data2_admin", "data2", "read")
    assert enforcer.enforce("data2_admin", "data2", "write")

    filter.v1 = []
    filter.v2 = ["read"]
    await enforcer.load_filtered_policy(filter)
    assert enforcer.enforce("alice", "data1", "read")
    assert not enforcer.enforce("alice", "data1", "write")
    assert not enforcer.enforce("alice", "data2", "read")
    assert not enforcer.enforce("alice", "data2", "write")
    assert not enforcer.enforce("bob", "data1", "read")
    assert not enforcer.enforce("bob", "data1", "write")
    assert not enforcer.enforce("bob", "data2", "read")
    assert not enforcer.enforce("bob", "data2", "write")
    assert enforcer.enforce("data2_admin", "data2", "read")
    assert not enforcer.enforce("data2_admin", "data2", "write")

    filter.v2 = ["write"]
    await enforcer.load_filtered_policy(filter)
    assert not enforcer.enforce("alice", "data1", "read")
    assert not enforcer.enforce("alice", "data1", "write")
    assert not enforcer.enforce("alice", "data2", "read")
    assert not enforcer.enforce("alice", "data2", "write")
    assert not enforcer.enforce("bob", "data1", "read")
    assert not enforcer.enforce("bob", "data1", "write")
    assert not enforcer.enforce("bob", "data2", "read")
    assert enforcer.enforce("bob", "data2", "write")
    assert not enforcer.enforce("data2_admin", "data2", "read")
    assert enforcer.enforce("data2_admin", "data2", "write")


async def test_update_policy(enforcer):
    assert enforcer.enforce("alice", "data1", "read")
    await enforcer.update_policy(
        ["alice", "data1", "read"], ["alice", "data1", "no_read"]
    )
    assert not enforcer.enforce("alice", "data1", "read")

    assert not enforcer.enforce("bob", "data1", "read")
    await enforcer.add_policy(["mike", "cookie", "eat"])
    await enforcer.update_policy(["mike", "cookie", "eat"], ["bob", "data1", "read"])
    assert enforcer.enforce("bob", "data1", "read")

    assert not enforcer.enforce("bob", "data1", "write")
    await enforcer.update_policy(["bob", "data1", "read"], ["bob", "data1", "write"])
    assert enforcer.enforce("bob", "data1", "write")

    assert enforcer.enforce("bob", "data2", "write")
    await enforcer.update_policy(["bob", "data2", "write"], ["bob", "data2", "read"])
    assert not enforcer.enforce("bob", "data2", "write")

    assert enforcer.enforce("bob", "data2", "read")
    await enforcer.update_policy(["bob", "data2", "read"], ["carl", "data2", "write"])
    assert not enforcer.enforce("bob", "data2", "write")

    assert enforcer.enforce("carl", "data2", "write")
    await enforcer.update_policy(
        ["carl", "data2", "write"], ["carl", "data2", "no_write"]
    )
    assert not enforcer.enforce("bob", "data2", "write")


async def test_update_policies(enforcer):
    old_rule_0 = ["alice", "data1", "read"]
    old_rule_1 = ["bob", "data2", "write"]
    old_rule_2 = ["data2_admin", "data2", "read"]
    old_rule_3 = ["data2_admin", "data2", "write"]

    new_rule_0 = ["alice", "data_test", "read"]
    new_rule_1 = ["bob", "data_test", "write"]
    new_rule_2 = ["data2_admin", "data_test", "read"]
    new_rule_3 = ["data2_admin", "data_test", "write"]

    old_rules = [old_rule_0, old_rule_1, old_rule_2, old_rule_3]
    new_rules = [new_rule_0, new_rule_1, new_rule_2, new_rule_3]

    await enforcer.update_policies(old_rules, new_rules)

    assert not enforcer.enforce("alice", "data1", "read")
    assert enforcer.enforce("alice", "data_test", "read")

    assert not enforcer.enforce("bob", "data2", "write")
    assert enforcer.enforce("bob", "data_test", "write")

    assert not enforcer.enforce("data2_admin", "data2", "read")
    assert enforcer.enforce("data2_admin", "data_test", "read")

    assert not enforcer.enforce("data2_admin", "data2", "write")
    assert enforcer.enforce("data2_admin", "data_test", "write")


async def test_update_filtered_policies(enforcer):
    assert not enforcer.enforce("alice", "data1", "write")

    await enforcer.update_filtered_policies([["alice", "data1", "write"]], 0, "alice")
    assert enforcer.enforce("alice", "data1", "write")
