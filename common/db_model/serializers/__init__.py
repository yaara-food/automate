from dataclasses import dataclass, field
from typing import Any, TypeAlias

from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm.attributes import NO_VALUE
from sqlmodel import SQLModel

from common.utils.enums import DBOperator


class BaseTable(SQLModel):
    def model_dump(
        self,
        *,
        include_relations: bool = False,
        max_depth: int = 1,
        _visited: set[int] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        base = super().model_dump(**kwargs)
        if not include_relations or max_depth <= 0:
            return base

        vid = id(self)
        visited = _visited or set()
        if vid in visited:
            return base
        visited.add(vid)

        insp = sa_inspect(self, raiseerr=False)
        if not insp:
            return base

        for rel in insp.mapper.relationships:
            key = rel.key
            if key in base:
                continue
            state = insp.attrs.get(key)
            if not state:
                continue

            loaded = state.loaded_value
            if loaded is NO_VALUE:
                continue

            if rel.uselist:
                base[key] = [
                    obj.model_dump(
                        include_relations=True,
                        max_depth=max_depth - 1,
                        _visited=visited,
                    )
                    for obj in (loaded or [])
                    if isinstance(obj, BaseTable)
                ]
            else:
                obj = loaded
                base[key] = (
                    obj.model_dump(
                        include_relations=True,
                        max_depth=max_depth - 1,
                        _visited=visited,
                    )
                    if isinstance(obj, BaseTable)
                    else obj
                )
        return base


RowLike: TypeAlias = BaseTable | dict[str, Any] | str


@dataclass
class DBQuery:
    opt: Any
    key: DBOperator
    value: Any


@dataclass
class FilterQuery:
    query: list[DBQuery] = field(default_factory=list)
    relation_model: bool = False
    sort: str | None = None
    count: bool = False
