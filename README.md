# Tortoise ORM Adapter for AsyncCasbin

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/thearchitector/casbin-tortoise-adapter/ci.yaml?label=tests&style=flat-square)
![PyPI - Downloads](https://img.shields.io/pypi/dm/casbin-tortoise-adapter?style=flat-square)
![GitHub](https://img.shields.io/github/license/thearchitector/casbin-tortoise-adapter?style=flat-square)
[![Buy a tree](https://img.shields.io/badge/Treeware-%F0%9F%8C%B3-lightgreen?style=flat-square)](https://ecologi.com/eliasgabriel?r=6128126916bfab8bd051026c)

This is an asynchronous adapter for [AsyncCasbin](https://pypi.org/project/asynccasbin) using Tortoise ORM.

## Installation

```sh
python3 -m pip install --user casbin-tortoise-adapter
# or via your favorite dependency manager, like Poetry
```

The current supported databases are [limited by Tortoise ORM](https://tortoise.github.io/databases.html), and include:

- PostgreSQL >= 9.4 (using `asyncpg`)
- SQLite (using `aiosqlite`)
- MySQL/MariaDB (using `asyncmy`)
- Microsoft SQL Server / Oracle (using `asyncodbc`)

## Documentation

The only configurable is the underlying Model used by `TortoiseAdapter`. While simple, it should be plenty to cover most use cases that one could come across. You can change the model by passing the `modelclass: CasbinRule` keyword argument to the adapter and updating the model in your Tortoise ORM init configuration.

The `modelclass` value must inherit from `casbin_tortoise_adapter.CasbinRule` to ensure that all the expected fields are present. A `TypeError` will throw if this is not the case.

A custom Model, combined with advanced configuration like show in the Tortoise ORM ["Two Databases" example](https://tortoise.github.io/examples/basic.html#two-databases), allow you to change where your authorization rules are stored (database, model name, etc.)

## Basic example

```python
from casbin import Enforcer
from tortoise import Tortoise

from casbin_tortoise_adapter import CasbinRule, TortoiseAdapter

async def main()
    # connect to db and generate schemas
    await Tortoise.init(
        db_url="postgres://postgres:password@test-db:5432/my_app",
        modules={"models": ["casbin_tortoise_adapter"]},
    )
    await Tortoise.generate_schemas()

    adapter = casbin_tortoise_adapter.TortoiseAdapter()
    e = casbin.Enforcer('path/to/model.conf', adapter, True)

    sub = "alice"  # the user that wants to access a resource.
    obj = "data1"  # the resource that is going to be accessed.
    act = "read"  # the operation that the user performs on the resource.

    if e.enforce(sub, obj, act):
        # permit alice to read data1
        pass
    else:
        # deny the request, show an error
        pass
```

### License

This project, like other adapters, is licensed under the [Apache 2.0 License](LICENSE).

This package is [Treeware](https://treeware.earth). If you use it in production, then we ask that you [**buy the world a tree**](https://ecologi.com/eliasgabriel?r=6128126916bfab8bd051026c) to thank us for our work. By contributing to my forest you’ll be creating employment for local families and restoring wildlife habitats.
