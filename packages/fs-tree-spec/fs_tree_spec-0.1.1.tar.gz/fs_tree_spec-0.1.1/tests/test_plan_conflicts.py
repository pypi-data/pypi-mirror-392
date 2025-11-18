from tree_adapter import plan_fs_from_tree
from pathlib import Path


def test_plan_existing_dir_and_file(tmp_path: Path):
    tree = {"root": {"file.txt": None, "dir": {}}}

    (tmp_path / "root").mkdir()
    (tmp_path / "root" / "file.txt").touch()
    (tmp_path / "root" / "dir").mkdir()

    plan = plan_fs_from_tree(tree, tmp_path)

    assert "root" in plan["dirs_exist"] or "" in plan["dirs_exist"]
    assert "root/file.txt" in plan["files_exist"]
    assert "root/dir" in plan["dirs_exist"]
    assert plan["conflicts"] == []

def test_plan_conflict_expected_file_found_dir(tmp_path: Path):
    tree = {"root": {"file.txt": None}}

    (tmp_path / "root").mkdir()
    (tmp_path / "root" / "file.txt").mkdir()

    plan = plan_fs_from_tree(tree, tmp_path)
    assert any("Expected file but found directory" in c for c in plan["conflicts"])

def test_plan_conflict_expected_dir_found_file(tmp_path: Path):
    tree = {"root": {"dir": {}}}

    (tmp_path / "root").mkdir()
    (tmp_path / "root" / "dir").touch()

    plan = plan_fs_from_tree(tree, tmp_path)
    assert any("Expected directory but found file" in c for c in plan["conflicts"])
