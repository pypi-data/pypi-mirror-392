# tilsit-config

`tilsit-config` is a lightweight Python utility for loading and managing
application configuration stored in **TOML** format.
It provides built-in support for **settings modeled as dataclasses**,
including boolean switches and selectable option lists.

This library is designed to simplify building UIs or CLI tools that allow
users to update configuration values safely.

---

## ✨ Features

- Load config values from a TOML file
- Automatically map TOML data into dataclass-based settings
- Built-in setting types:
  - `SettingBoolean` — boolean configuration values
  - `SettingOptions` — selectable values from predefined choices
- Track whether settings have changed
- Save user-modified settings back to the file
- Fully typed (mypy-friendly)

---

## 📦 Installation

```bash
pip install tilsit-config
```

---

## 🧩 Usage

### Define your settings

```python
from dataclasses import dataclass
from tilsit_config.settings import SettingBoolean, SettingOptions, SettingOption

@dataclass
class AppSettings:
    dark_mode: SettingBoolean
    language: SettingOptions
```

### Example `config.toml`

```toml
[settings]
dark_mode = { label = "Dark Mode", default_value = false, current_value = true }

[settings.language]
label = "Language"
default_value = "en"
current_value = "pl"

[[settings.language.options]]
value = "en"
display_str = "English"

[[settings.language.options]]
value = "pl"
display_str = "Polish"
```

### Loading and Saving Configuration

```python
from tilsit_config import load_config, save_settings

config_path = "config.toml"

config_dict, settings = load_config(config_path, AppSettings)

print(settings.dark_mode)
print(settings.language.current_value)

# Modify a setting in code
settings.dark_mode.current_value = False

# Save back to file
save_settings(config_path, settings)
```

---

## 🔍 Detect changes

```python
if settings.dark_mode.changed:
    print("Dark mode setting was changed.")
```

---

## 🗂 Structure of returned data

| Variable | Type | Description |
|---------|------|-------------|
| `config_dict` | `dict[str, Any]` | Raw TOML document |
| `settings` | Instance of provided dataclass or `None` | Mapped settings |

---

## 💡 Use cases

- TUI/GUI applications with persistent user preferences
- CLI tools with configuration overrides
- Games storing language/theme
- Feature toggles in config-driven apps

---

## 🤝 Contributing

Contributions, suggestions and issue reports are welcome!

---

## 📝 License

MIT License — see `LICENSE` for details.
