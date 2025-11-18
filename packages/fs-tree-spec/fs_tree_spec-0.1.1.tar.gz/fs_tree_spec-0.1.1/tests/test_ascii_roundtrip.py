from pathlib import Path
import json

from tree_adapter import (
    parse_ascii_tree,
    to_json,
    to_ascii_tree,
    plan_fs_from_tree,
    create_fs_from_tree,
)


ASCII_SPEC = """\
root/
├─ a.txt
├─ b.txt
└─ sub/
   ├─ c.txt
   └─ nested/
      └─ d.txt
"""


def test_parse_ascii_tree_structure():
    tree = parse_ascii_tree(ASCII_SPEC, include_root_label=True)

    # Basic shape
    assert "root" in tree
    root = tree["root"]
    assert isinstance(root, dict)

    assert ".git" not in root  # sanity: no weird extras
    assert "a.txt" in root and root["a.txt"] is None
    assert "b.txt" in root and root["b.txt"] is None
    assert "sub" in root and isinstance(root["sub"], dict)

    sub = root["sub"]
    assert "c.txt" in sub and sub["c.txt"] is None
    assert "nested" in sub and isinstance(sub["nested"], dict)
    assert "d.txt" in sub["nested"] and sub["nested"]["d.txt"] is None


def test_roundtrip_ascii_json():
    tree = parse_ascii_tree(ASCII_SPEC, include_root_label=True)

    # JSON serialization should succeed and be valid JSON
    json_str = to_json(tree)
    loaded = json.loads(json_str)

    assert "root" in loaded
    assert loaded["root"]["a.txt"] is None

    # ASCII rendering should not be empty
    ascii_out = to_ascii_tree(tree)
    assert "root/" in ascii_out
    assert "a.txt" in ascii_out
    assert "nested/" in ascii_out


def test_plan_fs_from_tree(tmp_path: Path):
    tree = parse_ascii_tree(ASCII_SPEC, include_root_label=True)

    plan = plan_fs_from_tree(tree, tmp_path)

    # No conflicts expected in a clean temp dir
    assert plan["conflicts"] == []

    # Ensure some expected paths are planned
    dirs_to_create = set(plan["dirs_to_create"])
    files_to_create = set(plan["files_to_create"])

    # Because the root maps directly under tmp_path, we expect:
    assert "root" in dirs_to_create or "root/" in dirs_to_create
    assert "root/a.txt" in files_to_create
    assert "root/sub/nested/d.txt" in files_to_create


def test_create_fs_from_tree(tmp_path: Path):
    tree = parse_ascii_tree(ASCII_SPEC, include_root_label=True)

    create_fs_from_tree(tree, tmp_path, create_files=True)

    root_dir = tmp_path / "root"
    assert root_dir.is_dir()

    # Files and subdirs exist
    assert (root_dir / "a.txt").is_file()
    assert (root_dir / "b.txt").is_file()

    sub_dir = root_dir / "sub"
    assert sub_dir.is_dir()
    assert (sub_dir / "c.txt").is_file()

    nested_dir = sub_dir / "nested"
    assert nested_dir.is_dir()
    assert (nested_dir / "d.txt").is_file()
