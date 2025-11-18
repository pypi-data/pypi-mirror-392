
# 📘 tree2cmd


### Convert text-based directory trees into real folders and files.

<p align="center">

  <!-- PyPI -->
  <a href="https://pypi.org/project/tree2cmd/">
    <img src="https://img.shields.io/pypi/v/tree2cmd.svg" alt="PyPI Version">
  </a>

  <!-- Python Versions -->
  <a href="https://pypi.org/project/tree2cmd/">
    <img src="https://img.shields.io/pypi/pyversions/tree2cmd.svg" alt="Python Versions">
  </a>

  <!-- License -->
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License">
  </a>

  <!-- Tests 100% -->
  <img src="https://img.shields.io/badge/tests-100%25-success" alt="Tests 100%">

  <!-- Platform -->
  <img src="https://img.shields.io/badge/platform-linux%20%7C%20macos-green" alt="Platforms">

  <!-- Downloads -->
  <img src="https://img.shields.io/pypi/dm/tree2cmd.svg" alt="PyPI Downloads">

  <!-- GitHub Actions: Tests -->
  <a href="https://github.com/ajmanjoma/tree2cmd/actions/workflows/python_tests.yml">
    <img src="https://github.com/ajmanjoma/tree2cmd/actions/workflows/python_tests.yml/badge.svg" alt="GitHub Tests Status">
  </a>

  <!-- GitHub Actions: TestPyPI -->
  <a href="https://github.com/ajmanjoma/tree2cmd/actions/workflows/testpypi.yml">
    <img src="https://github.com/ajmanjoma/tree2cmd/actions/workflows/testpypi.yml/badge.svg" alt="Publish to TestPyPI">
  </a>

  <!-- GitHub Actions: PyPI Publish -->
  <a href="https://github.com/ajmanjoma/tree2cmd/actions/workflows/publish.yml">
    <img src="https://github.com/ajmanjoma/tree2cmd/actions/workflows/publish.yml/badge.svg" alt="Publish to PyPI">
  </a>

  <!-- GitHub Actions: Auto Bump -->
  <a href="https://github.com/ajmanjoma/tree2cmd/actions/workflows/bump.yml">
    <img src="https://github.com/ajmanjoma/tree2cmd/actions/workflows/bump.yml/badge.svg" alt="Auto Version Bump">
  </a>

</p>

---

# 📑 Table of Contents

* [✨ Overview](#-overview)
* [🚀 Quick Start](#-quick-start)
* [📦 Installation](#-installation)
* [📂 Example Input → Output](#-example-input--output)
* [🔧 Usage Guide](#-usage-guide)
* [🧠 How It Works](#-how-it-works)
* [📚 Documentation](#-documentation)
* [🧪 Running Tests](#-running-tests)
* [🔄 Versioning & Publishing](#-versioning--publishing)
* [🤝 Contributing](#-contributing)
* [🗺️ Roadmap](#️-roadmap)
* [📄 License](#-license)
* [👤 Author](#-author)

---

# ✨ Overview

`tree2cmd` converts **text-based directory trees** (ASCII/Unicode) like:

```
Project/
├── src/
│   └── main.py
└── README.md
```

into **actual folders and files** using shell commands:

```
mkdir -p "Project/"
mkdir -p "Project/src/"
touch "Project/src/main.py"
touch "Project/README.md"
```

Perfect for:

✔ Rapid project scaffolding
✔ Teaching directory layouts
✔ DevOps automation
✔ Reproducible project templates
✔ Converting documentation examples into real directories

Fully tested across **ASCII trees**, **Unicode trees**, **emoji trees**, and **mixed indentation styles**.

---

# 🚀 Quick Start

### 1. Make `struct.txt`:

```
Project/
  src/
    main.py
  README.md
```

### 2. Convert to commands:

```bash
tree2cmd struct.txt
```

### 3. Actually create them:

```bash
tree2cmd struct.txt --run
```

---

# 📦 Installation

Stable release:

```bash
pip install tree2cmd
```

Latest development version:

```bash
pip install git+https://github.com/ajmanjoma/tree2cmd.git
```

---

# 📂 Example Input → Output

### Input:

```
📦 App/
  backend/
    api.py
  README.md
```

### Output:

```
mkdir -p "📦 App/"
mkdir -p "📦 App/backend/"
touch "📦 App/backend/api.py"
touch "📦 App/README.md"
```

### This **works for any**:

* ASCII tree
* Unicode tree
* Emoji directory
* Mixed indentation
* Minimal struct format
* Multi-root trees

---

# 🔧 Usage Guide

### Dry run (recommended):

```bash
tree2cmd struct.txt
```

### Execute commands:

```bash
tree2cmd struct.txt --run
```

### Save script:

```bash
tree2cmd struct.txt --save setup.sh
```

### Use standard input:

```bash
cat struct.txt | tree2cmd --stdin
```

### Show tree instead of commands:

```bash
tree2cmd struct.txt --tree
```

### Disable logs:

```bash
tree2cmd struct.txt --no-verbose
```

---

# 🧠 How It Works

tree2cmd uses a **3-stage pipeline**:

---

## 1️⃣ Parsing

Handles:

* ASCII trees (`|-`, `+--`, etc.)
* Unicode trees (`├──`, `│`, `└──`)
* Mixed whitespaces and unexpected characters
* Emojis and non-ASCII folder names
* Multi-root directories
* Deep nesting

Uses indentation and tree symbols to infer hierarchy.

---

## 2️⃣ Classification

Folder detection rules:

* Ends with `/` → **folder**
* Contains `.` → **file**
* Next line is more indented → **folder**
* Otherwise → **file**

---

## 3️⃣ Command Generation

Folders → `mkdir -p`
Files → `touch`

All paths:

* Are normalized
* Are quoted
* Escape shell-sensitive characters

---

# 📚 Documentation

| Topic          | File                   |
| -------------- | ---------------------- |
| Usage Guide    | `docs/usage.md`        |
| CLI Options    | `docs/cli.md`          |
| Parser Details | `docs/parser.md`       |
| API Reference  | `docs/api.md`          |
| FAQ            | `docs/faq.md`          |
| Contributing   | `docs/contributing.md` |
| Changelog      | `docs/changelog.md`    |

---

# 🧪 Running Tests

### Run all tests:

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

### With Makefile:

```bash
make test
```

Coverage: **100%** (parser + CLI)

---

# 🔄 Versioning & Publishing

### 1. Bump version automatically:

```bash
make version patch
# or minor / major
```

### 2. Build:

```bash
python -m build
```

### 3. Upload to PyPI:

```bash
twine upload dist/*
```

### 4. GitHub Actions (automatic):

* On tag push → build + test + publish
* On PR → run tests

Workflow located at:

```
.github/workflows/python-publish.yml
```

---

# 🤝 Contributing

All contributions are welcome!

1. Fork repo
2. Create a branch
3. Add tests for new features
4. Run tests
5. Open PR

See full guide:
📄 `docs/contributing.md`

---

# 🗺️ Roadmap

* [ ] Windows PowerShell support
* [ ] JSON/YAML → tree converter
* [ ] VSCode extension
* [ ] GUI visualizer
* [ ] Template engine (copy boilerplate files)

---

# 📄 License

MIT License — free for personal & commercial use.

---

# 👤 Author

**Antony Joseph Mathew**
📧 [antonyjosephmathew1@gmail.com](mailto:antonyjosephmathew1@gmail.com)
🌐 GitHub: [https://github.com/ajmanjoma/tree2cmd](https://github.com/ajmanjoma/tree2cmd)

