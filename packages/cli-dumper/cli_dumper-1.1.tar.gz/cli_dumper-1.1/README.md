# Dumper

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue)](https://www.python.org/)
[![Typer](https://img.shields.io/badge/CLI-typer-green)](https://typer.tiangolo.com/)
[![Rich](https://img.shields.io/badge/UI-rich-magenta)](https://github.com/Textualize/rich)
[![Tests](https://img.shields.io/badge/tests-pytest-yellow)](https://docs.pytest.org/)

**Dumper** is a simple CLI tool that merges multiple files into a single text file.
It supports patterns for inclusion and allows ignoring specific files or directories.

---

## ✨ Features
- 📂 Merge multiple files into one text file
- 🎯 Use glob patterns to include files (`.py`, `.txt`)
- 🚫 Ignore directories and specific files
- 🎨 Colored output powered by [rich](https://github.com/Textualize/rich)
- 🧪 Tested with `pytest`

---

## 🚀 Installation
### Recommended installing with **uv**:
```bash
uv tool install cli-dumper
```

### or from source:
```
git clone https://github.com/DasKaroWow/cli-dumper.git
cd cli-dumper
pip install -e .
```

---

## 📖 Usage

After installation, the CLI is available as `dumper`.

```bash
dumper .py --ignore-dirs venv --ignore-files test.py
```

This will:
- collect all `.py` files in the project (excluding `venv/` and `test.py`)
- merge their content into `project_dump.txt` in the current folder
- print a summary

---

## 🧑‍💻 Development

Run tests:

```bash
uv run pytest
```

Code style checks (if you add ruff/black):

```bash
uv run ruff check .
uv run ruff format .
```

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.
