from tree_adapter import parse_ascii_tree

def test_second_brain_dotenv_and_comments():
    ascii_spec = """\
root/
├─ .env                      # API keys + config (not committed)
├─ a.txt
└─ sub/
   └─ nested/
      └─ d.txt
"""
    tree = parse_ascii_tree(ascii_spec, include_root_label=True)

    assert "root" in tree
    root = tree["root"]

    # .env should be present as a filename
    assert ".env" in root
    # No bogus entry from the comment tail
    assert "config (not committed)" not in root
