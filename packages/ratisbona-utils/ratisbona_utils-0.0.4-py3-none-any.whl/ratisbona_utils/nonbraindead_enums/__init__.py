from enum import Enum

class ObjectEnum(Enum):
    def __new__(cls, argdict):
        if not isinstance(argdict, dict):
            raise TypeError(f"Expected a dict, got {type(argdict).__name__}")
        obj = object.__new__(cls)
        obj._value_ = len(cls.__members__)  #   # Platzhalter, wird im __init__ gesetzt
        for key, val in argdict.items():
            setattr(obj, key, val)
        return obj

    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_"))
        return f"<{self.__class__.__name__}.{self.name}: {attrs}>"

    @classmethod
    def findall(cls, **criteria):
        results = []
        for member in cls:
            if all(getattr(member, key, None) == val for key, val in criteria.items()):
                results.append(member)
        return results

    @classmethod
    def find(cls, **criteria):
        for member in cls:
            if all(getattr(member, key, None) == val for key, val in criteria.items()):
                return member
        return None

