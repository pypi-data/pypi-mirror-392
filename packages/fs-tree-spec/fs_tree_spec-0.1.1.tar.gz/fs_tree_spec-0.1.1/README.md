# 🪵 fs-tree-spec (tree_adapter)

**Translate between ASCII “tree” text, JSON/YAML tree specs, and real directory structures.**  
This tiny Python utility helps you describe, version, and reproduce directory layouts in a portable, human-readable way.

---

## ✨ Features

- Parse **ASCII “tree” text** (like `tree` command output) → nested Python structure
- Serialize / deserialize **JSON** and **YAML** tree specs
- Render a **Unicode tree** from structured data
- Validate naming rules (strict enforcement, no invalid characters)
- Compute a **dry-run plan** (`--plan`) of what would be created
- **Apply** (`--apply`) to actually build the filesystem
- Optional YAML support via `pip install fs-tree-spec[yaml]`

---

## 🧩 Installation

```bash
pip install fs-tree-spec
# or with YAML support:
pip install fs-tree-spec[yaml]
```

After installation, the CLI command `fs-tree-spec` becomes available.

---

## 🧭 Usage (CLI)

### Basic

```bash
# Plan creation from an ASCII spec
fs-tree-spec --from-ascii second_brain_tree.txt --root ./second-brain --plan

# Apply (actually create directories/files)
fs-tree-spec --from-ascii second_brain_tree.txt --root ./second-brain --apply

# Print as normalized ASCII and JSON
fs-tree-spec --from-ascii second_brain_tree.txt --print-tree --print-json
```

### From JSON or YAML

```bash
fs-tree-spec --from-json my_tree.json --plan
fs-tree-spec --from-yaml my_tree.yaml --apply
```

---

## 📜 Example Input

### ASCII tree text

```text
second-brain/
├─ .env                      # API keys + config (not committed)
├─ pyproject.toml
├─ README.md
├─ data/
│  ├─ raw/
│  │  └─ apple_notes_export/
│  ├─ attachments/
│  │  └─ ...
│  ├─ processed/
│  │  ├─ notes.jsonl
│  │  ├─ attachments.jsonl
│  │  └─ urls.jsonl
└─ notebooks/
   └─ exploration.ipynb
```

### Equivalent JSON

```json
{
  "second-brain": {
    ".env": null,
    "pyproject.toml": null,
    "README.md": null,
    "data": {
      "raw": { "apple_notes_export": {} },
      "attachments": {},
      "processed": {
        "notes.jsonl": null,
        "attachments.jsonl": null,
        "urls.jsonl": null
      }
    },
    "notebooks": {
      "exploration.ipynb": null
    }
  }
}
```

### Equivalent YAML

```yaml
second-brain:
  .env: null
  pyproject.toml: null
  README.md: null
  data:
    raw:
      apple_notes_export: {}
    attachments: {}
    processed:
      notes.jsonl: null
      attachments.jsonl: null
      urls.jsonl: null
  notebooks:
    exploration.ipynb: null
```

---

## 🧠 Naming Rules (Enforced)

1. Names are single path segments (no `/` or `\`).
2. Names must be non-empty after trimming.
3. Names cannot be `.`, `..`, `...`, or `…`.
4. Names cannot contain tree/box characters: `├└│─|+```
5. Inline comments begin with `" #"` and are ignored.
6. `"..."` and `"…"` lines are treated as placeholders only.
7. Conflicts between file vs. directory at same level raise an error.

---

## 🧪 Python API Example

```python
from tree_adapter import parse_ascii_tree, plan_fs_from_tree, create_fs_from_tree

ascii_spec = Path("second_brain_tree.txt").read_text()
tree = parse_ascii_tree(ascii_spec)

# Inspect
print(plan_fs_from_tree(tree, "./second-brain"))

# Create directories and files
create_fs_from_tree(tree, "./second-brain", create_files=True)
```

---

## 🛠️ Development

```bash
# Install in editable mode
pip install -e ".[yaml]"
```

Run locally:

```bash
python -m tree_adapter --from-ascii second_brain_tree.txt --plan
```

---

## 📦 Packaging

This project uses [PEP 621](https://peps.python.org/pep-0621/) metadata and can be built with:

```bash
python -m build
```

---

## ⚖️ License

MIT License © 2025 Stephen Wood

---

## 💡 Inspiration

- `tree` command output formatting  
- JSON/YAML for reproducible data models  
- Cross-tool “infrastructure as text” patterns

---

## 🪴 Example workflow

1. **Write a tree spec** in a `README.md` for documentation.
2. **Extract** the snippet and feed it to `fs-tree-spec --from-ascii`.
3. **Plan or apply** to generate the directory structure for new projects.
4. Optionally **export** the same spec to JSON or YAML for automation.

---

> “Describe once. Recreate anywhere.”
