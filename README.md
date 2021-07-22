# Tortoise ORM Adapter for AsyncCasbin

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/thearchitector/casbin-tortoise-adapter/CI?label=testing&style=flat-square)
![GitHub](https://img.shields.io/github/license/thearchitector/casbin-tortoise-adapter?style=flat-square)

This is an asynchronous adapter for [AsyncCasbin](https://pypi.org/project/asynccasbin) using Tortoise ORM.

## Installation

```sh
pip install casbin-tortoise-adapter
# or via your favorite dependency manager
```

The current supported databases are [limited by Tortoise ORM](https://tortoise.github.io/databases.html), and include:

- SQLite
- PostgreSQL >= 9.4 (using asyncpg)
- MySQL/MariaDB (using aiomysql)

## Documentation

The only possible configurable is the underlying Model used by `TortoiseAdapter`. While simple, it should be plenty to cover most use cases that one could come across. You can change the model by passing the `modelclass: CasbinRule` keyword argument to the adapter and updating the model in your Tortoise ORM init configuration.

The `modelclass` value must inherit from `casbin_tortoise_adapter.CasbinRule` to ensure that all the expected fields are present. A `TypeError` will throw if this is not the case.

A custom Model, combined with advanced configuration like show in the Tortoise ORM ["Two Databases" example](https://tortoise.github.io/examples/basic.html#two-databases), allow you to change where your authorization rules are stored (database, model name, etc.)

## Base Example

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
