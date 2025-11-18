from enum import Enum, EnumMeta
from typing import Type, cast


class OpenEnumMeta(EnumMeta):
    def __new__(cls, name, bases, classdict):
        # Only use the custom behavior for subclasses
        if name == "OpenEnum" and bases == (Enum,):
            return super().__new__(cls, name, bases, classdict)

        # Find the None member in classdict
        none_items = {k: v for k, v in classdict.items() if v is None}
        if len(none_items) > 1:
            raise ValueError("Only one None member is allowed in OpenEnum")
        if len(none_items) == 0:
            raise ValueError("An OpenEnum must have a None member")
        (unknown_key,) = none_items.keys()

        # Create a marker class for this specific enum
        class UnknownMarker:
            own_type: Type[Enum]
            own_members: set[Enum]

            def __eq__(self, other):
                return (
                    isinstance(other, self.own_type) and other not in self.own_members
                )

        # make it not a memmber
        classdict.pop(unknown_key)
        classdict._member_names.pop(unknown_key)

        # substitute the marker instad
        classdict._ignore.append(unknown_key)
        marker = UnknownMarker()
        classdict[unknown_key] = marker
        newcls = cast(Type[OpenEnum], super().__new__(cls, name, bases, classdict))

        # configure the marker
        marker.own_type = newcls
        marker.own_members = set(newcls)

        return newcls


class OpenEnum(Enum, metaclass=OpenEnumMeta):
    @classmethod
    def _missing_(cls, value):
        instance = object.__new__(cls)
        instance._name_ = "UNKNOWN"
        instance._value_ = value
        instance = cls._value2member_map_.setdefault(value, instance)
        return instance

    __match_args__ = ("value",)
