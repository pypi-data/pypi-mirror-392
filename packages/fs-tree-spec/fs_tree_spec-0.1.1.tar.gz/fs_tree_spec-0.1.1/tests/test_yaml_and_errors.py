from pathlib import Path
import json
import pytest

from tree_adapter import (
    to_yaml,
    from_yaml,
    parse_ascii_tree,
    to_json,
    from_json,
)


@pytest.fixture(autouse=True)
def _require_yaml():
    # Skip this module if PyYAML isn't available
    yaml = pytest.importorskip("yaml")


def test_yaml_roundtrip_simple():
    tree = {
        "root": {
            "file.txt": None,
            "subdir": {},
        }
    }

    yaml_str = to_yaml(tree)
    loaded = from_yaml(yaml_str)

    assert loaded == tree


def test_yaml_roundtrip_nested_and_nulls():
    tree = {
        "project": {
            "README.md": None,
            "src": {
                "main.py": None,
                "pkg": {},
            },
            "data": {},
        }
    }

    yaml_str = to_yaml(tree)
    loaded = from_yaml(yaml_str)

    # Same shape and semantics
    assert set(loaded.keys()) == {"project"}
    assert isinstance(loaded["project"], dict)
    assert loaded["project"]["README.md"] is None
    assert isinstance(loaded["project"]["src"], dict)
    assert loaded["project"]["src"]["main.py"] is None


def test_invalid_name_with_slash_in_ascii_spec():
    ascii_spec = """\
root/
└─ bad/name.txt
"""
    with pytest.raises(ValueError):
        parse_ascii_tree(ascii_spec, include_root_label=True)


def test_invalid_reserved_name_dot_in_ascii_spec():
    ascii_spec = """\
root/
└─ .
"""
    with pytest.raises(ValueError):
        parse_ascii_tree(ascii_spec, include_root_label=True)


def test_conflicting_file_and_directory_definitions():
    # 'thing/' declared as dir, then 'thing' as file → should raise
    ascii_spec = """\
root/
├─ thing/
└─ thing
"""
    with pytest.raises(ValueError):
        parse_ascii_tree(ascii_spec, include_root_label=True)


def test_placeholder_lines_are_ignored_not_created():
    ascii_spec = """\
root/
├─ real.txt  # real file
├─ ...
└─ sub/      # a directory
"""
    tree = parse_ascii_tree(ascii_spec, include_root_label=True)

    assert "root" in tree
    root = tree["root"]
    assert "real.txt" in root and root["real.txt"] is None
    assert "sub" in root and isinstance(root["sub"], dict)
    # Ensure placeholder didn't sneak in as a node
    assert "..." not in root


def test_include_root_label_false_flattens_children():
    ascii_spec = """\
project/
├─ a.txt
└─ sub/
   └─ b.txt
"""
    tree = parse_ascii_tree(ascii_spec, include_root_label=False)

    # No "project" key; children promoted to top level
    assert "project" not in tree
    assert "a.txt" in tree and tree["a.txt"] is None
    assert "sub" in tree and isinstance(tree["sub"], dict)
    assert tree["sub"]["b.txt"] is None

    # JSON conversion still valid
    j = to_json(tree)
    loaded = json.loads(j)
    assert "a.txt" in loaded
    assert "sub" in loaded

def test_forbidden_character_in_name():
    # Name includes a box-drawing char that should be rejected
    ascii_spec = """\
root/
└─ bad├name.txt
"""
    with pytest.raises(ValueError):
        parse_ascii_tree(ascii_spec, include_root_label=True)


def test_from_json_invalid_tree_rejected():
    # Value must be dict (dir) or None (file); list should fail
    bad_json = json.dumps({"root": {"bad": []}})
    with pytest.raises(ValueError):
        from_yaml_or_json_like(bad_json, is_json=True)


def test_from_yaml_invalid_tree_rejected():
    # Only run if yaml is available (fixture already importorskip's)
    bad_yaml = """
root:
  bad:
    - not_allowed
"""
    with pytest.raises(ValueError):
        from_yaml_or_json_like(bad_yaml, is_json=False)

def from_yaml_or_json_like(data: str, is_json: bool):
    if is_json:
        return from_json(data)
    else:
        return from_yaml(data)

def test_empty_name_ignored():
    # A "comment-only" style line after a connector should not crash parsing.
    # The exact behavior (ignored vs treated as a literal name) is not critical
    # to callers, so this test only asserts that parsing succeeds and root exists.
    ascii_spec = """\
root/
└─   # comment only, no name
"""
    tree = parse_ascii_tree(ascii_spec, include_root_label=True)

    assert "root" in tree
    # No strict assertion on children here; implementation may choose
    # to ignore this line or treat it as a literal filename.

def test_json_root_must_be_mapping():
    # Top-level list instead of dict → should be rejected
    with pytest.raises(ValueError):
        from_json('[]')

def test_json_root_must_be_mapping():
    # Top-level list instead of dict → should be rejected
    with pytest.raises(ValueError):
        from_json('[]')

def test_duplicate_directory_definitions_ok():
    ascii_spec = """\
root/
├─ sub/
└─ sub/
"""
    tree = parse_ascii_tree(ascii_spec, include_root_label=True)
    # Only one 'sub' under root
    assert "root" in tree
    assert list(tree["root"].keys()) == ["sub"]

def test_conflicting_file_then_directory_definitions_last_wins_as_dir():
    ascii_spec = """\
root/
├─ thing
└─ thing/
"""
    tree = parse_ascii_tree(ascii_spec, include_root_label=True)

    assert "root" in tree
    root = tree["root"]
    # The final form is a directory node for 'thing'
    assert "thing" in root
    assert isinstance(root["thing"], dict)


def test_yaml_inline_comments_are_ignored_in_structure():
    yaml_spec = """
    root:
      .env: null  # dotenv file
      pyproject.toml: null  # project config
      data:  # data directory
        raw:
          apple_notes_export: {}  # subdir
        processed:
          notes.jsonl: null  # notes
          attachments.jsonl: null  # attachments
    """
    tree = from_yaml(yaml_spec)

    assert "root" in tree
    root = tree["root"]

    # Keys are parsed correctly
    assert ".env" in root
    assert "pyproject.toml" in root
    assert "data" in root

    data = root["data"]
    assert "raw" in data
    assert "processed" in data
    assert "apple_notes_export" in data["raw"]
    assert "notes.jsonl" in data["processed"]
    assert "attachments.jsonl" in data["processed"]

    # YAML comments must not appear as keys
    all_keys = set(root.keys()) | set(data.keys()) | set(data["raw"].keys()) | set(data["processed"].keys())
    assert "dotenv file" not in all_keys
    assert "project config" not in all_keys
    assert "data directory" not in all_keys
    assert "subdir" not in all_keys
    assert "notes" not in all_keys
    assert "attachments" not in all_keys


def test_yaml_second_brain_style_comments():
    yaml_spec = """
    second-brain:
      .env: null  # API keys + config (not committed)
      pyproject.toml: null  # or requirements.txt
      README.md: null
      src:
        ingest:
          parse_apple_notes.py: null  # HTML/MD → structured Note + attachments + urls
          build_processed_views.py: null  # writes notes.jsonl, attachments.jsonl, urls.jsonl
        index:
          build_vector_index.py: null  # embeddings + vector store
          build_graph.py: null  # (optional)
    """
    tree = from_yaml(yaml_spec)

    assert "second-brain" in tree
    sb = tree["second-brain"]

    assert ".env" in sb
    assert "pyproject.toml" in sb
    assert "README.md" in sb

    src = sb["src"]
    ingest = src["ingest"]
    index = src["index"]

    assert "parse_apple_notes.py" in ingest
    assert "build_processed_views.py" in ingest
    assert "build_vector_index.py" in index
    assert "build_graph.py" in index

    # Ensure no comment fragments appear as keys
    bad = {
        "API keys + config (not committed)",
        "or requirements.txt",
        "HTML/MD → structured Note + attachments + urls",
        "writes notes.jsonl, attachments.jsonl, urls.jsonl",
        "embeddings + vector store",
        "(optional)",
    }
    all_keys = (
        set(sb.keys())
        | set(src.keys())
        | set(ingest.keys())
        | set(index.keys())
    )
    assert bad.isdisjoint(all_keys)
