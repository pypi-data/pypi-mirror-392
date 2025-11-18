# Yark 🌳

[![PyPI version](https://badge.fury.io/py/yark-scaffold.svg)](https://badge.fury.io/py/yark)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

**A Terraform-inspired YAML-based directory scaffolding tool with state management.**

Define your project structure in YAML, and Yark safely creates and updates it — never touching files it doesn't own.

---

## ✨ Features

- 📝 **YAML-defined structures** - Clean, readable project definitions
- 🛡️ **State management** - Terraform-style tracking of managed resources
- 🔒 **Safe updates** - Never deletes your manual files
- 🎨 **Colored diff output** - See what will be created/deleted with visual highlights
- 👁️ **Dry-run mode** - Preview changes before applying
- 🌲 **Tree visualization** - Beautiful terminal output with [Rich](https://github.com/Textualize/rich)
- 🔄 **Idempotent** - Run multiple times safely

---

## 🚀 Quick Start

### Installation
```bash
pip install yark-scaffold
```

### Basic Usage

**1. Define your structure in YAML:**
```yaml
# project-structure.yaml
project/:
  - src/:
      - main.py
      - utils.py
      - tests/:
          - test_main.py
  - docs/:
      - README.md
  - config.yaml
```

**2. Create the structure:**
```bash
yark create -f project-structure.yaml -p ./my-project
```

**Output:**
```
✓ Structure created successfully in './my-project'
✓ State file created: .yark.state (tracks 7 resources)
```

**3. Add your own files (safely):**
```bash
cd my-project
touch .env              # Your file
touch local_notes.txt   # Your file
```

**Yark will never touch these files!** ✅

**4. Update the structure:**

Modify your YAML, then:
```bash
yark update -f project-structure.yaml -p ./my-project --dry-run
```

See colored preview:
```
📁 my-project/
├── 📄 .env                    (unchanged)
├── 📄 local_notes.txt         (unchanged)
├── 📄 new_file.py             (new)     ← Green
├── 📄 old_file.py             (deleted) ← Red
└── 📁 src/
    └── ...
```

---

## 📖 Commands

### `create` - Initialize new structure

Creates directories and files from YAML.
```bash
yark create -f <yaml-file> -p <target-path> [--dry-run]
```

**Examples:**
```bash
# Create in current directory
yark create -f structure.yaml

# Create in specific directory
yark create -f structure.yaml -p ./new-project

# Preview without creating
yark create -f structure.yaml -p ./new-project --dry-run
```

**What it does:**
- Creates all files and folders from YAML
- Generates `.yark.state` file to track what it created

---

### `update` - Sync structure with YAML

Updates existing structure to match YAML (only touches managed files).
```bash
yark update -f <yaml-file> -p <target-path> [--dry-run]
```

**Examples:**
```bash
# Update structure
yark update -f structure.yaml -p ./my-project

# Preview changes
yark update -f structure.yaml -p ./my-project --dry-run
```

**What it does:**
- Creates new files/folders from YAML
- Deletes files/folders that were removed from YAML (only if managed)
- **Ignores files not in state** (your manual files are safe!)
- Updates `.yark.state`

---

### `list` - Show directory tree

Displays current directory structure.
```bash
yark list -p <directory>
```

**Examples:**
```bash
# List current directory
yark list

# List specific directory
yark list -p ./my-project
```

---

## 🔒 State Management (The Key Feature)

Yark uses a **Terraform-style state file** (`.yark.state`) to track which files it manages.

### How It Works:

**Initial create:**
```bash
yark create -f structure.yaml -p ./project
# Creates: .yark.state tracking all created files
```

**You add your own files:**
```bash
touch ./project/.env
touch ./project/notes.txt
# These are NOT in .yark.state
```

**Update with modified YAML:**
```bash
yark update -f structure.yaml -p ./project
# Only modifies files in .yark.state
# Your .env and notes.txt are IGNORED ✓
```

### Safety Guarantees:

✅ **Only deletes managed files** (those in `.yark.state`)  
✅ **Ignores your manual files** completely  
✅ **Won't run update without state** (prevents accidents)  
✅ **Clear error messages** if state is missing  

---

## 📝 YAML Structure Format

### Basic Structure
```yaml
root/:
  - file1.txt
  - file2.py
  - subfolder/:
      - nested_file.txt
```

### Rules:

- **Folders end with `/`** (required)
- **Files are strings** in folder lists
- **Nested folders** use dict or list format
- **Empty folders** use empty list: `folder/: []`

### Examples:

**Simple project:**
```yaml
project/:
  - README.md
  - main.py
  - config.json
```

**Nested structure:**
```yaml
webapp/:
  - frontend/:
      - src/:
          - App.jsx
          - index.js
      - public/:
          - index.html
  - backend/:
      - api/:
          - routes.py
      - main.py
  - docker-compose.yml
```

**Mixed format:**
```yaml
project/:
  src/:                    # Dict style
    - main.py
    - utils.py
  tests/:                  # List style
    - test_main.py
  - README.md             # Root files
```

---

## 🎯 Use Cases

- **Bootstrap new projects** with consistent structure
- **Team project templates** everyone uses same layout
- **Monorepo management** maintain folder structure across repos
- **Documentation** YAML serves as structure documentation
- **CI/CD** automate project setup in pipelines

---

## 🛠️ Development

### Setup
```bash
git clone https://github.com/youssef-abbih/yark.git
cd yark
pip install -e .
pip install -r requirements.txt
```

### Run Tests
```bash
pytest tests/ -v

# With coverage
pytest tests/ --cov=yark --cov-report=term-missing
```

### Project Structure
```
yark/
├── yark/              # Source code
│   ├── cli.py         # Command-line interface
│   ├── parser.py      # YAML parsing
│   ├── builder.py     # Structure creation
│   ├── updater.py     # Structure updates
│   ├── scanner.py     # Directory scanning
│   ├── state.py       # State management
│   └── ...
├── tests/             # Test suite
│   ├── fixtures/      # Test YAML files
│   └── test_*.py
└── README.md
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure tests pass: `pytest`
5. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- Inspired by Terraform's state management approach
- YAML for clean, readable configuration

---

## 🗺️ Roadmap

- [ ] File content templating
- [ ] Interactive YAML generator (`yark init`)
- [ ] `.yarkignore` support
- [ ] Remote state backends
- [ ] Project templates library

---

**Start structuring your projects with Yark — safe, simple, and state-managed!** 🚀