import pytest

from sshcore.metadata import (
    parse_metadata_comment,
    parse_tags,
    format_metadata_comments,
)
from sshcore.models import HostBlock


def test_parse_metadata_comment_handles_valid_and_invalid():
    assert parse_metadata_comment("Host foo") == (None, None)
    assert parse_metadata_comment("# comment") == (None, None)
    assert parse_metadata_comment("# @tags missing colon") == (None, None)

    key, value = parse_metadata_comment("#   @TaGs:  prod , web  ")
    assert key == "tags"
    assert value == "prod , web"


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("", []),
        ("frontend", ["frontend"]),
        ("prod, web, critical", ["prod", "web", "critical"]),
        ("prod, ,  web ,", ["prod", "web"]),
    ],
)
def test_parse_tags_normalizes_values(raw, expected):
    assert parse_tags(raw) == expected


def test_format_metadata_comments_round_trip():
    assert format_metadata_comments([]) == []
    assert format_metadata_comments(["prod", "web"]) == ["# @tags: prod, web"]


def test_host_block_tag_helpers_and_listing_names(tmp_path):
    host = HostBlock(
        patterns=["app-server", "app-*", "db?[0-9]"],
        source_file=tmp_path / "config",
        lineno=10,
    )
    host.add_tag("Prod")
    host.add_tag("prod")  # duplicate ignored case-insensitively
    host.add_tag("Web")
    assert host.tags == ["Prod", "Web"]
    assert host.has_tag("web")
    host.remove_tag("PROD")
    assert host.tags == ["Web"]

    # Only literal patterns should appear
    assert host.names_for_listing == ["app-server"]
