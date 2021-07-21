import pytest

from casbin_tortoise_adapter import CasbinRule, RuleFilter, TortoiseAdapter


def test_bad_modelclass():
    class BadModel:
        pass

    with pytest.raises(TypeError):
        TortoiseAdapter(modelclass=BadModel)


@pytest.mark.asyncio
async def test_enforcer_basic(mock_data, enforcer):
    await enforcer.load_policy()

    assert enforcer.enforce("alice", "data1", "read")
    assert not enforcer.enforce("alice", "data1", "write")
    assert not enforcer.enforce("bob", "data1", "read")
    assert not enforcer.enforce("bob", "data1", "write")
    assert enforcer.enforce("bob", "data2", "write")
    assert not enforcer.enforce("bob", "data2", "read")
    assert enforcer.enforce("alice", "data2", "read")
    assert enforcer.enforce("alice", "data2", "write")


@pytest.mark.asyncio
async def test_add_policy(enforcer):
    assert not enforcer.enforce("eve", "data3", "read")
    res = await enforcer.add_policies(
        (("eve", "data3", "read"), ("eve", "data4", "read"))
    )
    assert res
    assert enforcer.enforce("eve", "data3", "read")
    assert enforcer.enforce("eve", "data4", "read")


@pytest.mark.asyncio
async def test_add_policies(enforcer):
    assert not enforcer.enforce("eve", "data3", "read")
    res = await enforcer.add_permission_for_user("eve", "data3", "read")
    assert res
    assert enforcer.enforce("eve", "data3", "read")


@pytest.mark.asyncio
async def test_save_policy(enforcer):
    assert not enforcer.enforce("alice", "data4", "read")

    model = enforcer.get_model()
    model.clear_policy()
    model.add_policy("p", "p", ["alice", "data4", "read"])
    await enforcer.get_adapter().save_policy(model)
    assert enforcer.enforce("alice", "data4", "read")


@pytest.mark.asyncio
async def test_remove_policy(enforcer):
    assert not enforcer.enforce("alice", "data5", "read")
    await enforcer.add_permission_for_user("alice", "data5", "read")
    assert enforcer.enforce("alice", "data5", "read")
    await enforcer.delete_permission_for_user("alice", "data5", "read")
    assert not enforcer.enforce("alice", "data5", "read")


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_remove_filtered_policy(mock_data, enforcer):
    await enforcer.load_policy()

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

    # await enforcer.add_permission_for_user("alice", "data6", "delete")
    # await enforcer.add_permission_for_user("bob", "data6", "delete")
    # await enforcer.add_permission_for_user("eve", "data6", "delete")
    # assert enforcer.enforce("alice", "data6", "delete")
    # assert enforcer.enforce("bob", "data6", "delete")
    # assert enforcer.enforce("eve", "data6", "delete")
    # await enforcer.remove_filtered_policy(0, "alice", None, "delete")
    # assert not enforcer.enforce("alice", "data6", "delete")
    # await enforcer.remove_filtered_policy(0, None, None, "delete")
    # assert not enforcer.enforce("bob", "data6", "delete")
    # assert not enforcer.enforce("eve", "data6", "delete")


def test_str(enforcer):
    rule = CasbinRule(ptype="p", v0="alice", v1="data1", v2="read")
    assert str(rule) == "p, alice, data1, read"
    rule = CasbinRule(ptype="p", v0="bob", v1="data2", v2="write")
    assert str(rule) == "p, bob, data2, write"
    rule = CasbinRule(ptype="p", v0="data2_admin", v1="data2", v2="read")
    assert str(rule) == "p, data2_admin, data2, read"
    rule = CasbinRule(ptype="p", v0="data2_admin", v1="data2", v2="write")
    assert str(rule) == "p, data2_admin, data2, write"
    rule = CasbinRule(ptype="g", v0="alice", v1="data2_admin")
    assert str(rule) == "g, alice, data2_admin"


def test_repr(enforcer):
    rule = CasbinRule(ptype="p", v0="alice", v1="data1", v2="read")
    assert repr(rule) == '<CasbinRule None: "p, alice, data1, read">'


@pytest.mark.asyncio
async def test_filtered_policy(mock_data, enforcer):
    await enforcer.load_policy()

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
