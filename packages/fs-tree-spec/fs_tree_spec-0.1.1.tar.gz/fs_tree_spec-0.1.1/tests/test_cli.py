import json
import subprocess
import sys
from pathlib import Path
from typing import List

import pytest


ASCII_SPEC = """\
root/
├─ a.txt
└─ sub/
   └─ b.txt
"""


def run_cli(tmp_path: Path, args: List[str]) -> subprocess.CompletedProcess:
    """
    Helper to run `python -m tree_adapter` with given args.
    """
    cmd = [sys.executable, "-m", "tree_adapter"] + args
    return subprocess.run(
        cmd,
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )


def test_cli_plan_from_ascii(tmp_path: Path):
    spec_path = tmp_path / "tree.txt"
    spec_path.write_text(ASCII_SPEC, encoding="utf-8")

    # Default behavior with --plan (since no other flags -> plan)
    proc = run_cli(
        tmp_path,
        [
            "--from-ascii",
            str(spec_path),
            "--root",
            str(tmp_path / "out"),
        ],
    )

    assert proc.returncode == 0, proc.stderr

    # Expect JSON plan on stdout
    stdout = proc.stdout.strip()
    assert stdout, "Expected non-empty stdout from plan"

    # Last JSON block should parse; we tolerate extra newlines
    # Find last '{' to avoid any header text if present
    start = stdout.rfind("{")
    assert start != -1, f"Expected JSON in stdout, got: {stdout!r}"
    plan = json.loads(stdout[start:])

    assert "dirs_to_create" in plan
    assert "files_to_create" in plan
    # basic sanity: something about root/sub is planned
    assert any("root" in d for d in plan["dirs_to_create"]) or any(
        p.startswith("root") for p in plan["files_to_create"]
    )


def test_cli_apply_creates_structure(tmp_path: Path):
    spec_path = tmp_path / "tree.txt"
    spec_path.write_text(ASCII_SPEC, encoding="utf-8")

    out_root = tmp_path / "created"

    proc = run_cli(
        tmp_path,
        [
            "--from-ascii",
            str(spec_path),
            "--root",
            str(out_root),
            "--apply",
        ],
    )

    assert proc.returncode == 0, proc.stderr
    # Check some observable output
    assert "Created structure under" in proc.stdout

    # Verify filesystem effects
    assert (out_root / "root").is_dir()
    assert (out_root / "root" / "a.txt").is_file()
    assert (out_root / "root" / "sub").is_dir()
    assert (out_root / "root" / "sub" / "b.txt").is_file()

def test_cli_print_tree_and_json(tmp_path: Path):
    spec_path = tmp_path / "tree.txt"
    spec_path.write_text(ASCII_SPEC, encoding="utf-8")

    proc = run_cli(
        tmp_path,
        [
            "--from-ascii",
            str(spec_path),
            "--root",
            str(tmp_path / "out"),
            "--print-tree",
            "--print-json",
        ],
    )

    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    # Basic sanity: both formats present
    assert "root/" in out
    assert '"root"' in out

def test_cli_apply_no_files_creates_only_dirs(tmp_path: Path):
    spec_path = tmp_path / "tree.txt"
    spec_path.write_text(ASCII_SPEC, encoding="utf-8")

    out_root = tmp_path / "created"

    proc = run_cli(
        tmp_path,
        [
            "--from-ascii",
            str(spec_path),
            "--root",
            str(out_root),
            "--apply",
            "--no-files",
        ],
    )

    assert proc.returncode == 0, proc.stderr
    # root + sub dirs exist
    assert (out_root / "root").is_dir()
    assert (out_root / "root" / "sub").is_dir()
    # files should NOT exist
    assert not (out_root / "root" / "a.txt").exists()
    assert not (out_root / "root" / "sub" / "b.txt").exists()

def test_cli_missing_ascii_file_errors(tmp_path: Path):
    missing = tmp_path / "does_not_exist.txt"

    proc = run_cli(
        tmp_path,
        [
            "--from-ascii",
            str(missing),
            "--root",
            str(tmp_path / "out"),
            "--plan",
        ],
    )

    assert proc.returncode != 0
    # We expect an error message from our main() handler
    assert "Error loading spec" in proc.stderr or "No such file" in proc.stderr

@pytest.mark.skipif("yaml" not in sys.modules, reason="PyYAML not installed")
def test_cli_print_yaml(tmp_path: Path):
    spec_path = tmp_path / "tree.txt"
    spec_path.write_text(ASCII_SPEC, encoding="utf-8")

    proc = run_cli(
        tmp_path,
        [
            "--from-ascii",
            str(spec_path),
            "--root",
            str(tmp_path / "out"),
            "--print-yaml",
        ],
    )

    assert proc.returncode == 0, proc.stderr
    # YAML-ish output: key followed by colon
    assert "root:" in proc.stdout

def test_cli_from_json_plan(tmp_path: Path):
    tree = {"root": {"a.txt": None}}
    json_path = tmp_path / "tree.json"
    json_path.write_text(json.dumps(tree), encoding="utf-8")

    proc = run_cli(
        tmp_path,
        [
            "--from-json",
            str(json_path),
            "--root",
            str(tmp_path / "out"),
            "--plan",
        ],
    )

    assert proc.returncode == 0, proc.stderr

    stdout = proc.stdout.strip()
    assert stdout, "Expected non-empty stdout from plan"

    # Find the last JSON object in stdout (defensive in case of extra prints)
    start = stdout.rfind("{")
    assert start != -1, f"Expected JSON in stdout, got: {stdout!r}"
    plan = json.loads(stdout[start:])

    assert "files_to_create" in plan
    # We expect the planned files to include our a.txt under root
    assert any("a.txt" in path for path in plan["files_to_create"])


def test_cli_from_yaml_plan(tmp_path: Path):
    pytest.importorskip("yaml")
    import yaml as _yaml

    tree = {"root": {"a.txt": None}}
    yaml_path = tmp_path / "tree.yaml"
    yaml_path.write_text(_yaml.safe_dump(tree), encoding="utf-8")

    proc = run_cli(
        tmp_path,
        [
            "--from-yaml",
            str(yaml_path),
            "--root",
            str(tmp_path / "out"),
            "--plan",
        ],
    )

    assert proc.returncode == 0, proc.stderr
    assert '"a.txt"' in proc.stdout or "a.txt" in proc.stdout

