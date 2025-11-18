from __future__ import annotations
import dataclasses
import json
import datetime
import uuid
from typing import Callable

from mypy.nodes import TypeAlias

Predicate: TypeAlias = Callable[[object], bool]
DictSerializer: TypeAlias = Callable[[object], dict]

def type_to_testfunction(type_: type) -> Predicate:
    """
    Creates a predicate that checks if an object is of the given type.
    :param type_: The type to check against.
    :return: A predicate function that returns True if the object is of the given type.
    """
    def testfunction(obj: object) -> bool:
        """
        Predicate function that checks if the object is of the given type.
        :param obj: The object to check.
        :return: True if the object is of the given type, False otherwise.
        """
        return isinstance(obj, type_)
    return testfunction

datetime_predicate = type_to_testfunction(datetime.datetime)
def datetime_serialize(obj: datetime.datetime) -> dict:
    """
    Serializes a datetime object to ISO format.
    :param obj: The datetime object to serialize.
    :return: A dictionary with the ISO formatted datetime string.
    """
    return {"__datetime__": obj.isoformat()}

def pydantic_predicate(obj: object) -> bool:
    """
    Predicate that checks if an object is a Pydantic model.
    :param obj: The object to check.
    :return: True if the object is a Pydantic model, False otherwise.
    """
    return hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')) and hasattr(obj, '__class__') and hasattr(obj.__class__, '__name__')

def pydantic_serialize(obj: object) -> dict:
    """
    Serializes a Pydantic model to a dictionary.
    :param obj: The Pydantic model to serialize.
    :return: A dictionary representation of the Pydantic model.
    """
    return obj.to_dict()

uuid_predicate = type_to_testfunction(uuid.UUID)
def uuid_serialize(obj: uuid.UUID) -> dict:
    """
    Serializes a UUID object to a string.
    :param obj: The UUID object to serialize.
    :return: A dictionary with the UUID string.
    """
    return {"__uuid__": str(obj)}


@dataclasses.dataclass
class UniversalDictEncoder(json.JSONEncoder):
    _registry: dict = dataclasses.field(default_factory=dict)

    def register(self, testfunction: Predicate, serializer: DictSerializer ) -> UniversalDictEncoder:
        self._registry[testfunction] = serializer
        return self

    def default(self, obj):
        for testfunction, serializer in self._registry.items():
            if testfunction(obj):
                return serializer(obj)
        return super().default(obj)

