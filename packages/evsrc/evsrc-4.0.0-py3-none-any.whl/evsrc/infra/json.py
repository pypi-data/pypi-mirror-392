import abc
import json
from dataclasses import MISSING, fields, is_dataclass
from enum import Enum
from types import NoneType, UnionType
from typing import Any, Type, TypeVar, cast, get_args, get_origin

from evsrc.lib.model import Aggregate, ChangeEvent, EventRecord, Version
from evsrc.lib.ports import AggregateParser, EventBatchParser

T = TypeVar("T")


class DataclassJDictMapper:
    """Map dataclasses to jsonable dicts or construct it from one"""

    JSON_BASIC = (float, int, str, bool)
    __dataclasses = {}

    @classmethod
    def to_jdict(cls, value: Any) -> dict[str, Any]:
        """Convert a Value object to a jsonable dict"""

        if not is_dataclass(value):
            raise TypeError(f'Value "value" is not a dataclass')

        data = {}
        for field in fields(value):
            value_ = getattr(value, field.name)
            if field.default is not MISSING and field.default == value_:
                continue
            if (
                field.default_factory is not MISSING
                and value_ == field.default_factory()
            ):
                continue

            data[field.name] = cls._encode_value(value_)
        return data

    @classmethod
    def _encode_value(cls, value: Any):
        if is_dataclass(value) and not isinstance(value, type):
            print(f"Value is {value}")
            data = cls.to_jdict(value)
            print(data)
            return data

        if isinstance(value, Enum):
            return value.name
        if isinstance(value, list):
            return [cls._encode_value(item) for item in value]
        if isinstance(value, tuple):
            return tuple([cls._encode_value(item) for item in value])
        if isinstance(value, dict):
            return {key: cls._encode_value(value_) for key, value_ in value.items()}
        if type(value) not in cls.JSON_BASIC:
            raise TypeError(f"Value {value} is not jsonable")

        return value

    @classmethod
    def from_jdict(cls, data: dict[str, Any], data_class: Type) -> Any:
        if not is_dataclass(data_class):
            raise TypeError(f"Type {data_class} is not a dataclass")

        cls.__dataclasses[data_class.__name__] = data_class
        init_values = {}
        for field in fields(data_class):
            if field.name in data:
                init_values[field.name] = cls._decode_value(
                    data[field.name], field.type
                )
            else:
                if field.default is MISSING and field.default_factory is MISSING:
                    raise ValueError(
                        f"Field {field.name} is missing and has no default value."
                    )

        return data_class(**init_values)

    @classmethod
    def _decode_value(cls, value, field_typing):
        origin = get_origin(field_typing)
        args = get_args(field_typing)
        if origin is None:  # It is a class
            if is_dataclass(field_typing):
                return cls.from_jdict(value, cast(type, field_typing))

            if type(field_typing) is str:
                if field_typing not in cls.__dataclasses:
                    raise TypeError(f'Type "{field_typing}" not found to be decoded')

                return cls._decode_value(value, cls.__dataclasses[field_typing])

            if issubclass(field_typing, Enum):
                return (
                    field_typing[value] if type(value) is str else field_typing(value)
                )

            if field_typing not in cls.JSON_BASIC:
                raise TypeError(f"Value {value} is not a jsonable object")

            return value

        args = get_args(field_typing)
        if origin is list:
            return [cls._decode_value(item, args[0]) for item in value]

        if origin is dict:
            return {key: cls._decode_value(val, args[1]) for key, val in value.items()}

        if origin is tuple:
            if len(args) == 2 and args[1] == ...:
                return tuple([cls._decode_value(item, args[0]) for item in value])
            else:
                return tuple(
                    [
                        cls._decode_value(item, _typing)
                        for _typing, item in zip(args, value)
                    ]
                )

        if origin is dict and args[1] != Any:
            return {
                key: cls._decode_value(value_, args[1]) for key, value_ in value.items()
            }

        if origin is UnionType:
            for type_ in args:
                try:
                    return cls._decode_value(value, type_)
                except Exception as e:
                    ...

        if (field_typing is NoneType or field_typing is None) and value is None:
            return

        raise TypeError(f"Not possible to construct {value} from {field_typing}")


class JsonableAggregate(Aggregate, abc.ABC):
    """Interface which assert aggregate is loaded or converted to jsonable dict,
    ChangeEvents of the Aggregate must be embeded in the class."""

    @classmethod
    def decode_event(cls, jdict: dict[str, Any]) -> Any:
        """Constructor of aggregate events"""
        data = jdict.copy()
        event_cls = getattr(cls, data.pop("__event__"))
        return DataclassJDictMapper.from_jdict(data, event_cls)

    @classmethod
    def encode_event(cls, event: ChangeEvent) -> dict[str, Any]:
        data = DataclassJDictMapper.to_jdict(event)
        data["__event__"] = event.__class__.__name__
        return data

    @abc.abstractmethod
    def as_jdict(self) -> dict[str, Any]:
        """Convert the aggregate to a jsonable dict"""

    @classmethod
    @abc.abstractmethod
    def from_jdict(cls, data: dict[str, Any]) -> "JsonableAggregate":
        """Convert a dict into DictMapped aggregate"""


class JsonAggregateParser(AggregateParser):
    def __init__(self, cls: Type[JsonableAggregate]):
        self._cls = cls

    def encode(self, aggregate: Aggregate) -> bytes:
        mapped = cast(JsonableAggregate, aggregate)

        return json.dumps(mapped.as_jdict()).encode()

    def decode(self, raw: bytes) -> Aggregate:
        data = json.loads(raw)
        return self._cls.from_jdict(data)


class JsonEventBatchParser(EventBatchParser):
    def __init__(
        self,
        cls: Type[JsonableAggregate],
    ):
        self._cls = cls

    def encode(self, records: list[EventRecord]) -> bytes:
        if not records:
            return b""

        tss = []
        event_dicts = []
        version_value = records[0].version.value - 1
        ts = records[0].version.timestamp
        for record in records:
            if record.version.value - version_value != 1:
                raise ValueError(
                    f"There is a gap between {record.version.value} and {version_value}"
                )
            tss.append(record.version.timestamp - ts)
            event_dicts.append(self._cls.encode_event(record.event))
            ts = record.version.timestamp
            version_value += 1

        return json.dumps(
            {
                "from": [records[0].version.value, records[0].version.timestamp],
                "tss": tss,
                "events": event_dicts,
            }
        ).encode()

    def decode(self, raw: bytes) -> list[EventRecord]:
        records = []
        data = json.loads(raw)
        version_value, ts = data.pop("from")
        for inc, event_data in zip(data.pop("tss"), data.pop("events")):
            ts += inc
            records.append(
                EventRecord(
                    Version(version_value, ts),
                    cast(ChangeEvent, self._cls.decode_event(event_data)),
                )
            )
            version_value += 1

        return records
