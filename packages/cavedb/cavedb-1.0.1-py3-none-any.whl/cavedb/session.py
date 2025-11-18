import asyncio
import logging
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any, AsyncGenerator, Generic, Literal, TypeVar
from uuid import UUID

import orjson
from aiofiles import open, os

from .entity import Entity, EntityField, FieldClause

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Entity)


class BaseQuery(Generic[T]):
    """Abstract base query"""

    def __init__(self, session: "Session", entity_class: type[T]):
        self._session = session
        self._entity_class = entity_class

        # Common DML feature properties
        self._limit: int = -1
        self._where_clauses: list[FieldClause] = []

    def where(self, *where_clauses: FieldClause):
        """Filter query by clauses through disjunction"""

        for clause in where_clauses:
            if not isinstance(clause, FieldClause):
                raise TypeError(
                    f"WHERE clauses must use Entity field definitions to be of type FieldClause, wrong type {type(clause)}"
                )

        self._where_clauses.extend(where_clauses)
        return self


class SelectQuery(Generic[T], BaseQuery[T]):

    def limit(self, value: int = -1):
        """Set a limit on amount of selected entities

        Empty argument or negative values disable limit"""

        self._limit = value
        return self

    async def first(self) -> T | None:
        """Get the first occurence of Entity model or None if not found"""

        self._limit = 1

        async for entity in self._session._execute_select(self):
            return entity

        return None

    async def all(self) -> list[T]:
        """Get all query results as a list"""

        results: list[T] = []

        async for entity in self._session._execute_select(self):
            results.append(entity)

        return results

    async def stream(self) -> AsyncGenerator[T, None]:
        """Stream query results"""

        async for entity in self._session._execute_select(self):
            yield entity


class DeleteQuery(Generic[T], BaseQuery[T]):
    pass


class Session:
    """DB access session supporting transactions and fully async

    Usage:
    ```python
    import asyncio
    from cavedb import Session

    async def main():
        async with Session() as session:
            # Simulate operations with objects
            user = User(name="jeff")
            session.add(user)

            # If you want to sync changes to file right now
            await session.commit()

            user.age = 30
            # Need to register models on session after each commit
            session(add)
            await session.commit()

            # Example SELECT query
            await session.select(User).where()

        # Will automatically call .commit() on context exit
        # Errors will rollback and skip saving to file

    asyncio.run(main())
    ```
    """

    def __init__(self, root_filepath: Path | str = "./"):
        self._upsert_entities: defaultdict[str, list[Entity]] = defaultdict(list)
        self._delete_entities: defaultdict[str, list[Entity]] = defaultdict(list)
        self._root_filepath = Path(root_filepath)
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exctype, exc, tb):
        if not exctype:
            if self._upsert_entities or self._delete_entities:
                logger.debug("BEGIN transaction (implicit on session close)")
                await self.commit()
        else:
            logger.debug("ROLLBACK transaction")

    async def _ensure_table_file(self, table_filename: str):
        """Ensures that a table data file exists and creates it otherwise"""

        table_filename = self._root_filepath / table_filename
        if not await os.path.exists(table_filename):
            logging.info(f"Table {table_filename} file missing, creating empty")
            async with open(table_filename, "a") as file:
                await file.write("")

    async def _read_table_file(
        self,
        table_name: str,
    ) -> AsyncGenerator[dict[str, Any], None]:
        table_filename = self._root_filepath / f"{table_name.lower()}.jsonl"
        await self._ensure_table_file(table_filename)
        async with open(table_filename) as file:
            async for line in file:
                if line.strip():
                    yield orjson.loads(line)

    async def _write_table_file(
        self,
        table_name: str,
        added_entities: list[Entity],
        update_entities: list[Entity],
        delete_entities: list[Entity],
    ):
        table_filename = self._root_filepath / f"{table_name.lower()}.jsonl"
        table_tmp_filename = self._root_filepath / f"{table_name.lower()}.tmp"

        async with open(
            table_tmp_filename,
            "w",
        ) as tmpfile:
            async for entity_data in self._read_table_file(table_name):
                skip = False
                for delete_entity in delete_entities:
                    if UUID(entity_data["_id"]) == delete_entity.id:
                        logger.debug(
                            f"DELETE FROM {table_name} WHERE {table_name}.id = {repr(delete_entity.id)};"
                        )
                        skip = True
                        break

                if skip:
                    continue

                replace = None
                for update_entity in update_entities:
                    if UUID(entity_data["_id"]) == update_entity.id:
                        logger.debug(
                            f"UPDATE {table_name} SET {repr(update_entity)} WHERE {table_name}.id = {repr(update_entity.id)};"
                        )
                        replace = update_entity
                        break

                if replace:
                    await tmpfile.write(
                        orjson.dumps(asdict(replace)).decode("utf-8") + "\n"
                    )
                    continue

                await tmpfile.write(orjson.dumps(entity_data).decode("utf-8") + "\n")

        async with (
            open(
                table_tmp_filename,
                "r",
            ) as tmpfile,
            open(table_filename, "w") as file,
        ):
            async for line in tmpfile:
                await file.write(line)

            if added_entities:
                logger.debug(
                    f"INSERT INTO {table_name} VALUES {', '.join([repr(entity) for entity in added_entities])};"
                )
                entity_jsons = [
                    orjson.dumps(asdict(entity)).decode("utf-8") + "\n"
                    for entity in added_entities
                ]
                await file.writelines(entity_jsons)

        await os.unlink(table_tmp_filename)

    def select(self, entity_class: type[T]):
        return SelectQuery[T](self, entity_class)

    def delete(self, entity: T):
        """Register entity for deletion"""
        self._delete_entities[entity._get_table_name()].append(entity)

    async def _execute_select(
        self, query: SelectQuery[T]
    ) -> AsyncGenerator[list[Entity], None]:
        table_name = query._entity_class._get_table_name()

        logger.debug(
            f"SELECT FROM {query._entity_class._get_table_name()} WHERE {' AND '.join([str(clause) for clause in query._where_clauses])} LIMIT {query._limit};"
        )

        row_index = 0
        async for entity_data in self._read_table_file(table_name):
            if query._limit > 0 and row_index >= query._limit:
                return

            keep = True
            for clause in query._where_clauses:
                main: Literal["left", "right"] | None = None
                if (
                    isinstance(clause.left, EntityField)
                    and clause.left.entity_class == query._entity_class
                ):
                    main = "left"
                elif (
                    isinstance(clause.right, EntityField)
                    and clause.right.entity_class == query._entity_class
                ):
                    main = "right"

                if main:
                    if main == "left":
                        main_side = clause.left
                        other_side = clause.right
                    else:
                        main_side = clause.right
                        other_side = clause.left

                    if clause.operator == "eq":
                        if main_side.type(entity_data[main_side.name]) != other_side:
                            keep = False
                            break
                    elif clause.operator == "ne":
                        if main_side.type(entity_data[main_side.name]) == other_side:
                            keep = False
                            break
                    elif clause.operator == "gt":
                        if main_side.type(entity_data[main_side.name]) <= other_side:
                            keep = False
                            break
                    elif clause.operator == "lt":
                        if main_side.type(entity_data[main_side.name]) >= other_side:
                            keep = False
                            break
                    elif clause.operator == "ge":
                        if main_side.type(entity_data[main_side.name]) < other_side:
                            keep = False
                            break
                    elif clause.operator == "le":
                        if main_side.type(entity_data[main_side.name]) > other_side:
                            keep = False
                            break
                    elif clause.operator == "invert":
                        if entity_data[main_side.name]:
                            keep = False
                            break
                    else:
                        raise NotImplementedError(
                            f"This clause operator {clause.operator} is not supported yet"
                        )

                else:
                    if clause.operator == "eq":
                        if clause.left != clause.right:
                            keep = False
                            break
                    elif clause.operator == "ne":
                        if clause.left == clause.right:
                            keep = False
                            break
                    elif clause.operator == "gt":
                        if clause.left <= clause.right:
                            keep = False
                            break
                    elif clause.operator == "lt":
                        if clause.left >= clause.right:
                            keep = False
                            break
                    elif clause.operator == "ge":
                        if clause.left < clause.right:
                            keep = False
                            break
                    elif clause.operator == "le":
                        if clause.left > clause.right:
                            keep = False
                            break
                    elif clause.operator == "invert":
                        if clause.left:
                            keep = False
                            break
                    else:
                        raise NotImplementedError(
                            f"This clause operator {clause.operator} is not supported yet"
                        )

            if not keep:
                continue

            id = entity_data.pop("_id")
            entity = query._entity_class(**entity_data)
            entity._id = id
            row_index += 1

            logger.debug(f"\tRESULT {repr(entity)};")
            yield entity

    def add(self, entity: Entity):
        """Register created or updated instance in session"""
        self._upsert_entities[entity._get_table_name()].append(entity)

    async def commit(self):
        """Commit changes in registered entities"""

        added: defaultdict[str, list[Entity]] = defaultdict(list)
        updated: defaultdict[str, list[Entity]] = defaultdict(list)

        for table_name, entities in self._upsert_entities.items():
            async for entity_data in self._read_table_file(table_name):
                for entity in entities:
                    if entity.id == UUID(entity_data["_id"]):
                        updated[table_name].append(entity)

            for entity in entities:
                if entity not in updated[table_name]:
                    added[table_name].append(entity)

        for table_name in added.keys() | updated.keys() | self._delete_entities.keys():
            await self._write_table_file(
                table_name,
                added[table_name],
                updated[table_name],
                self._delete_entities[table_name],
            )

        self._upsert_entities.clear()
        self._delete_entities.clear()

        logger.debug("COMMIT transaction;")
