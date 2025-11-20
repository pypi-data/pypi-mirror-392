import textwrap
from pathlib import Path

import pytest

from sshcore.config import (
    append_host_block,
    format_host_block,
    format_host_block_with_metadata,
    parse_config_files,
    remove_host_block,
    replace_host_block_with_metadata,
)


def test_parse_config_files_handles_includes_and_metadata(tmp_path):
    main = tmp_path / "ssh_config"
    extras_dir = tmp_path / "extras"
    extras_dir.mkdir()
    included = extras_dir / "extra.conf"

    main.write_text(
        textwrap.dedent(
            """\
            # file header
            # @tags: prod, primary
            Host prod-server
                HostName prod.example.com
                User ubuntu

            Include extras/*.conf
            """
        )
    )

    included.write_text(
        textwrap.dedent(
            """\
            # random comment
            # @tags: staging, web
            Host staging-*
                HostName staging.example.com
                Port 2222
            """
        )
    )

    blocks = parse_config_files([main])
    assert len(blocks) == 2

    by_source = {block.source_file: block for block in blocks}
    prod = by_source[main]
    assert prod.metadata_lineno == 1
    assert prod.tags == ["prod", "primary"]
    assert prod.options["HostName"] == "prod.example.com"
    assert prod.options["User"] == "ubuntu"

    staging = by_source[included]
    assert staging.tags == ["staging", "web"]
    assert staging.options["Port"] == "2222"


def test_format_host_block_helpers_include_metadata():
    formatted = format_host_block(["foo"], [("HostName", "foo.example.com")])
    assert formatted.startswith("Host foo")
    assert formatted.endswith("\n")

    formatted_meta = format_host_block_with_metadata(
        ["foo"], [("HostName", "foo")], tags=["prod", "web"]
    )
    assert formatted_meta.splitlines()[0] == "# @tags: prod, web"
    assert "Host foo" in formatted_meta


def test_append_host_block_creates_files_and_backups(tmp_path):
    target = tmp_path / "config"
    backup = append_host_block(
        target,
        ["new-host"],
        [("HostName", "new.example.com")],
        tags=["prod", "blue"],
    )
    assert backup is None
    initial = target.read_text()
    assert "# @tags: prod, blue" in initial
    assert initial.endswith("\n")

    backup2 = append_host_block(
        target,
        ["second"],
        [("HostName", "second.example.com")],
    )
    assert backup2 is not None
    assert backup2.exists()
    combined = target.read_text()
    assert "second.example.com" in combined
    assert "\n\nHost second" in combined


def test_replace_host_block_with_metadata_preserves_tags(tmp_path):
    target = tmp_path / "config"
    append_host_block(
        target,
        ["legacy"],
        [("HostName", "legacy.local"), ("User", "ubuntu")],
        tags=["legacy", "prod"],
    )
    block = next(iter(parse_config_files([target])))
    replace_host_block_with_metadata(
        target,
        block,
        ["legacy"],
        [("HostName", "updated.local"), ("Port", "22")],
    )
    content = target.read_text()
    assert "# @tags: legacy, prod" in content
    assert "updated.local" in content
    assert "Port 22" in content
    assert "User ubuntu" not in content


def test_remove_host_block_creates_backup_and_cleans_blank_lines(tmp_path):
    target = tmp_path / "config"
    target.write_text(
        textwrap.dedent(
            """\
            # @tags: keep
            Host keep
                HostName keep.local

            # @tags: remove
            Host remove
                HostName remove.local
            """
        )
    )
    blocks = parse_config_files([target])
    remove_block = next(block for block in blocks if "remove" in block.patterns)

    backup = remove_host_block(target, remove_block)
    assert backup is not None and backup.exists()

    content = target.read_text()
    assert "remove.local" not in content
    assert "# @tags: keep" in content
    assert "\n\n\n" not in content
