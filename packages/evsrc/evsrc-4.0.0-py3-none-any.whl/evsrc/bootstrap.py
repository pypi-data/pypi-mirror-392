from typing import Type
from evsrc.infra.json import JsonAggregateParser, JsonEventBatchParser, JsonableAggregate
from evsrc.lib.ports import FileSystem
from evsrc.lib.stores import EventBatchStore, SnapshotStore
from .lib.repos import AggregateRepository


def new_json_aggregate_repo(
    cls: Type[JsonableAggregate],
    fs: FileSystem,
    max_length: int = 50,
    max_time: float = 28 * 24 * 3600.0,
) -> AggregateRepository:
    aggregate_name = cls.__name__
    batchs = EventBatchStore(fs, JsonEventBatchParser(cls))
    snaps = SnapshotStore(fs, JsonAggregateParser(cls))
    return AggregateRepository(aggregate_name, batchs, snaps, max_length, max_time)
