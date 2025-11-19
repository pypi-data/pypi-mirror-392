from dataclasses import dataclass, field
from typing import Generic, TypeVar, Union

TValue = TypeVar("TValue")


@dataclass
class Setting(Generic[TValue]):
    label: str
    default_value: TValue
    current_value: TValue
    old_value: TValue = field(init=False)

    @property
    def changed(self) -> bool:
        return self.current_value != self.old_value


@dataclass
class SettingOption:
    value: str
    display_str: str


@dataclass
class SettingOptions(Setting[str]):
    default_value: str
    current_value: str
    old_value: str = field(init=False)
    options: list[SettingOption]


@dataclass
class SettingBoolean(Setting[bool]):
    default_value: bool
    current_value: bool
    old_value: bool = field(init=False)

    def __bool__(self):
        return self.current_value


SettingType = Union[SettingOptions, SettingBoolean]
