from dataclasses import fields, is_dataclass
from typing import Any, ClassVar, Protocol, Type, cast

import tomlkit

from .settings import SettingBoolean, SettingOption, SettingOptions, SettingType


class Dataclass(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Any]]


def load_config(
    config_file: str,
    settings_cls: Type[Dataclass] | None = None,
) -> tuple[dict[str, Any], Dataclass | None]:
    with open(config_file, mode="rt", encoding="utf-8") as f:
        config_doc = tomlkit.load(f)

    config_dict = cast(dict[str, Any], config_doc)

    if is_dataclass(settings_cls):
        settings_values: dict[str, Any] = {}

        for field in fields(settings_cls):
            d = config_dict["settings"][field.name]

            setting: SettingType

            if field.type is SettingOptions:
                options = [SettingOption(**option) for option in d["options"]]
                setting = SettingOptions(
                    **{k: v for k, v in d.items() if k != "options"}, options=options
                )
            else:
                setting = SettingBoolean(**d)

            settings_values[field.name] = setting

        settings = settings_cls(**settings_values)
    else:
        settings = None

    return config_dict, settings


def save_settings(config_file: str, settings: Dataclass):
    with open(config_file, mode="rt", encoding="utf-8") as f:
        config_doc = tomlkit.load(f)

    config_dict = cast(dict[str, Any], config_doc)

    for field in fields(settings):
        setting: SettingType = getattr(settings, field.name)
        config_dict["settings"][field.name]["current_value"] = setting.current_value

    with open(config_file, mode="wt", encoding="utf-8") as f:
        tomlkit.dump(config_doc, f)  # type: ignore[arg-type]
