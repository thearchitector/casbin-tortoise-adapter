import asyncio
import os

import pytest
from casbin import AsyncEnforcer
from tortoise import Tortoise

from casbin_tortoise_adapter import CasbinRule, TortoiseAdapter


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def adapter():
    host: str = os.getenv("POSTGRES_HOST", "postgres")

    # connect to db and generate schemas
    await Tortoise.init(
        {
            "connections": {
                "default": f"postgres://postgres:password@{host}:5432/casbin"
            },
            "apps": {"my_app": {"models": ["casbin_tortoise_adapter"]}},
        },
        _create_db=True,
    )
    await Tortoise.generate_schemas()

    # insert test cases into the db, ensure to cleanup afterwards
    try:
        yield TortoiseAdapter()
    finally:
        await Tortoise._drop_databases()
        await Tortoise.close_connections()


@pytest.fixture
async def mock_data():
    await CasbinRule.all().delete()
    await CasbinRule.bulk_create(
        [
            CasbinRule(ptype="p", v0="alice", v1="data1", v2="read"),
            CasbinRule(ptype="p", v0="data2_admin", v1="data2", v2="read"),
            CasbinRule(ptype="p", v0="bob", v1="data2", v2="write"),
            CasbinRule(ptype="p", v0="data2_admin", v1="data2", v2="write"),
            CasbinRule(ptype="g", v0="alice", v1="data2_admin"),
        ]
    )


@pytest.fixture
async def enforcer(adapter, mock_data):
    e = AsyncEnforcer("tests/rbac_model.conf", adapter)
    await e.load_policy()
    yield e
