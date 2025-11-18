from dataclasses import dataclass, field
from types import NoneType, UnionType
from typing import Any, Generic, Literal, TypeVar
from uuid import UUID, uuid4

type FieldOperator = Literal["eq", "gt", "lt", "ge", "le", "ne", "invert"]

OPERATOR_SYMBOLS: dict[FieldOperator, str] = {
    "eq": "==",
    "ne": "!=",
    "gt": ">",
    "lt": "<",
    "ge": ">=",
    "le": "<=",
    "invert": "~",
}
UNARY_OPERATORS: tuple[FieldOperator, ...] = ("invert",)


class FieldClause:
    """Some clause based on Entitie's fields"""

    def __init__(self, operator: FieldOperator, left: Any, right: Any):
        self.operator: FieldOperator = operator
        self.left = left
        self.right = right

    def __repr__(self):
        if self.operator in UNARY_OPERATORS:
            return f"FieldClause({OPERATOR_SYMBOLS[self.operator]}{repr(self.left)})"

        return f"FieldClause({repr(self.left)} {OPERATOR_SYMBOLS[self.operator]} {repr(self.right)})"

    def __str__(self):
        if isinstance(self.left, EntityField):
            left = f"{self.left.entity_class._get_table_name()}.{self.left.name}"
        else:
            left = repr(self.left)

        if self.operator in UNARY_OPERATORS:
            return f"{OPERATOR_SYMBOLS[self.operator]}{repr(self.left)}"

        if isinstance(self.right, EntityField):
            right = f"{self.right.entity_class._get_table_name()}.{self.right.name}"
        else:
            right = repr(self.right)

        return f"{left} {OPERATOR_SYMBOLS[self.operator]} {right}"


T = TypeVar("T", bound=type)


class EntityField(Generic[T]):
    """A proxy representing Entity's field to build clauses upon"""

    def __init__(self, entity_class: type["Entity"], name: str, type: type[T]):
        self.entity_class = entity_class
        self.name = name
        self.type = type

    def __repr__(self):
        return f"EntityField({self.entity_class._get_table_name()}.{self.name} {self.type})"

    def _check_clause_types(self, value):
        if self.type != type(value):
            raise TypeError(
                f"Field {self.entity_class._get_table_name()}.{self.name} type is incompatible with provided value type {type(value)}"
            )

    def __eq__(self, value):
        self._check_clause_types(value)
        return FieldClause("eq", self, value)

    def __ne__(self, value):
        self._check_clause_types(value)
        return FieldClause("ne", self, value)

    def __gt__(self, value):
        self._check_clause_types(value)
        return FieldClause("gt", self, value)

    def __lt__(self, value):
        self._check_clause_types(value)
        return FieldClause("lt", self, value)

    def __ge__(self, value):
        self._check_clause_types(value)
        return FieldClause("ge", self, value)

    def __le__(self, value):
        self._check_clause_types(value)
        return FieldClause("le", self, value)

    def __invert__(self):
        return FieldClause("invert", self, None)


class EntityMeta(type):
    """Entity metaclass providing a way to address EntityFields and build FieldClauses from fields operations"""

    def __getattribute__(cls, name: str) -> EntityField:
        dataclass_fields = None
        try:
            # Get __dataclass_fields__ without recursion
            dataclass_fields = type.__getattribute__(cls, "__dataclass_fields__")
        except AttributeError:
            pass

        if dataclass_fields and name in dataclass_fields:
            field_type = cls.__dataclass_fields__[name].type
            if isinstance(field_type, UnionType):
                field_types = []
                for arg in field_type.__args__:
                    if arg != NoneType:
                        field_types.append(arg)

                if len(field_types) > 1:
                    raise TypeError(
                        "Entity fields must be of a single type or Optional (UnionType with NoneType)"
                    )

                field_type = field_types[0]

            return EntityField(cls, name, field_type)

        if name == "id":
            return EntityField(cls, "_id", UUID)

        return type.__getattribute__(cls, name)


@dataclass
class Entity(metaclass=EntityMeta):
    """Base abstract ORM data entity with db-side UUID

    Usage:
    ```python
    from dataclasses import dataclass, field
    from cavedb import Entity

    @dataclass
    class User(Entity):
        name: str
        age: int | None = field(default=None)

    user = User("jeff")
    user.age = 30
    ```
    """

    _id: UUID = field(default_factory=uuid4, init=False)

    def __getattr__(cls, name):
        if name == "id":
            return UUID(str(cls._id))

    @classmethod
    def _get_table_name(cls) -> str:
        """Entity table name derived from class"""
        return cls.__qualname__
