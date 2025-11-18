# cavedb

An async JSONL-based **database** with ORM bindings to Python dataclasses.

Name is stylised all-lowercase.

## Features

Define table models as dataclasses-subclasses of Entity to begin using ORM features.

```python
from cavedb import Entity

# A user.jsonl table, will create user.jsonl file
@dataclass
class User(Entity):
    usename: str                           # Required field
    age: int | None = field(default=None)  # Nullable field
```

Start using **threadsafe** and **fully async** database Sessions to query and write data to storage.

```python
from cavedb import Session

# Zero configuration required
async with Session() as session:
    user = await session.select(User).first()
    # -> User(_id=UUID(bf911f00-117e-4a66-8f62-e0429492d5b0), username='john', age=25)
```

Full typing support through Generics. You will never have to guess what is returned.

```python
session.select(User)          # -> <SelectQuery>
session.select(User).first()  # -> <User | None>
session.select(User).stream() # -> <AsyncGenerator[User, None]>
session.select(User).all()    # -> <list[User]>
User.id                       # -> <EntityField>
User.id != None               # -> <FieldClause>
```

Stored data is in **JSONL** format files one-per-table and _easily human-readable_!

```json
{"_id":"bf911f00-117e-4a66-8f62-e0429492d5b0","username":"john","age":25}
{"_id":"fc4d0ada-6ea0-423e-a096-973a3a2779ee","username":"julia","age":27}
{"_id":"b3f647bf-d15e-4891-b383-2951f099a9a3","username":"jacob","age":null}
```

Create queries with ease:

```python
users = await session.select(User).where(
    User.name != "john",
    User.age != None,
).all()
# -> [User(_id=UUID(fc4d0ada-6ea0-423e-a096-973a3a2779ee), username='julia', age=27)]
```

Upsert objects through session:

```python
async with Session() as session:
    user = User(name="jack", age=50)
    user.id # -> UUID(...) - Readonly, already managed for you

    # Use just as any other dataclass
    user.age -= 23

    # Register in session for upserting
    session.add(user)

    # Commit changes (autocommit is set on session close - if no exceptions occur)
    await session.commit()

    # Choose your own paradigm: Commit As You Go / Unit Of Work
```

Threadsafe and true async when working with persistant storage in files.

## Limitations

1. Required PK field `id` as `UUID`.
2. Missing FK relations and JOIN/select in load operations
