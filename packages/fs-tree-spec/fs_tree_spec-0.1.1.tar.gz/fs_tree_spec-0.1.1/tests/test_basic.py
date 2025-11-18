from pathlib import Path
from tree_adapter import parse_ascii_tree, to_json, plan_fs_from_tree

from pathlib import Path
import json
import sys

import pytest

from tree_adapter import (
    create_fs_from_ascii,
    create_fs_from_json,
    create_fs_from_yaml,
    to_yaml,
)

def test_parse_and_plan(tmp_path: Path):
    ascii_spec = """\
root/
├─ a.txt
└─ sub/
   └─ b.txt
"""
    tree = parse_ascii_tree(ascii_spec, include_root_label=True)

    # JSON round-trip smoke test
    j = to_json(tree)
    assert "root" in j

    plan = plan_fs_from_tree(tree, tmp_path)
    assert "root/a.txt" in [f"{p}" for p in plan["files_to_create"]] or "a.txt" in plan["files_to_create"]
    assert not plan["conflicts"]

from tree_adapter import (
    create_fs_from_ascii,
    create_fs_from_json,
    create_fs_from_yaml,
    to_yaml,
)

def test_create_fs_from_ascii_wrapper(tmp_path: Path):
    ascii_spec = """\
root/
└─ f.txt
"""
    root = create_fs_from_ascii(ascii_spec, tmp_path)
    assert (root / "root" / "f.txt").is_file()


def test_create_fs_from_json_wrapper(tmp_path: Path):
    tree = {"root": {"f.txt": None}}
    json_text = json.dumps(tree)
    root = create_fs_from_json(json_text, tmp_path)
    assert (root / "root" / "f.txt").is_file()


@pytest.mark.skipif("yaml" not in sys.modules, reason="PyYAML not installed")
def test_create_fs_from_yaml_wrapper(tmp_path: Path):
    tree = {"root": {"f.txt": None}}
    yaml_text = to_yaml(tree)
    root = create_fs_from_yaml(yaml_text, tmp_path)
    assert (root / "root" / "f.txt").is_file()
