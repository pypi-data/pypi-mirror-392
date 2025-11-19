# tilsit-i18n

`tilsit-i18n` is a lightweight wrapper around Python’s built‑in `gettext` module.
Its purpose is to make internationalization **simple and runtime‑switchable**
with a single global translation object.

```python
from pathlib import Path
from tilsit_i18n import tr

tr.localedir = Path(__file__).parent / "locale"
tr.language = "pl"
print(tr("Hello"))
```
---

## ✨ Features

- Simple, minimalistic interface: **use `tr("message")` anywhere**
- Runtime language switching (`tr.language = "pl"`)
- Built on `gettext` — full `.po`/`.mo` compatibility
- Safe fallbacks:
  - English (`"en"`) as default
  - `NullTranslations` when `.mo` not found
- Automatic logging of missing translation files
- Zero dependencies beyond Python + `loguru`

---

## 📦 Installation

```bash
pip install tilsit-i18n
```

---

## 🧩 Usage

### Initialize the translation directory

```python
from pathlib import Path
from tilsit_i18n import tr

tr.localedir = Path(__file__).parent / "locale"
```

### Set language

```python
tr.language = "pl"
```

### Translate messages

```python
print(tr("Hello world"))
```

When the language is `"en"` (default), the message is returned unchanged.

---

## 🔧 Generating `.mo` files

Translations are edited in `.po` files and compiled to `.mo`.

Compile:

```bash
msgfmt.py -o messages.mo messages
```

---

## 🧪 Example `.po`

```po
msgid "Hello"
msgstr "Cześć"

msgid "Exit"
msgstr "Wyjście"
```

---

## ⚠️ Error handling

`tilsit-i18n` logs common issues:

- Missing `localedir`
- Missing `.mo` file for selected language

Example log:

```
ERROR localedir is not initialized
ERROR .mo file is not found
```

---

## 💡 Internals (how it works)

The core object:

```python
@dataclass
class Translation:
    default_language = "en"
    default_domain = "messages"

    localedir: Path | None = None
    _language: str = "en"
    _gnutranslations = gettext.NullTranslations()
```

It:

- Tracks language
- Loads the correct `GNUTranslations` object
- Falls back to English when needed
- Is callable: `tr("message")`

---

## 🤝 Contributing

Issues, pull requests and suggestions are welcome!

---

## 📝 License

MIT License — see `LICENSE` for details.
