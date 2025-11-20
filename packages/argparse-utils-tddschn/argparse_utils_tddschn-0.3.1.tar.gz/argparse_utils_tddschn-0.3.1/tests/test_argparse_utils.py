import argparse

import pytest

from argparse_utils import (
    preset_arguments,
    remove_argument,
    replace_argument_names,
)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="prog")
    parser.add_argument("-c", "--config")
    parser.add_argument("--dry-run", action="store_true")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--force", action="store_true")
    group.add_argument("--safe", action="store_true")
    return parser


def test_remove_argument_deletes_all_references():
    parser = make_parser()

    remove_argument(parser, "--dry-run")

    assert "--dry-run" not in parser._option_string_actions
    assert "--dry-run" not in parser.format_help()


def test_remove_argument_from_mutually_exclusive_group():
    parser = make_parser()

    remove_argument(parser, "--force")

    group_actions = parser._mutually_exclusive_groups[0]._group_actions
    assert all(action.dest != "force" for action in group_actions)


def test_remove_argument_raises_for_missing_action():
    parser = make_parser()

    with pytest.raises(ValueError):
        remove_argument(parser, "--nonexistent")


def test_replace_argument_names_overwrites_all_option_strings():
    parser = make_parser()

    replace_argument_names(parser, "--config", ["-C", "--configuration"])

    assert "-C" in parser._option_string_actions
    assert "--configuration" in parser._option_string_actions
    assert parser._option_string_actions["-C"].option_strings == [
        "-C",
        "--configuration",
    ]


def test_replace_argument_names_checks_conflicts():
    parser = make_parser()

    with pytest.raises(ValueError):
        replace_argument_names(parser, "--config", ["--dry-run"])


def test_preset_arguments_seed_defaults_for_values_and_flags():
    parser = make_parser()

    preset_arguments(parser, ["--config", "foo.ini", "--dry-run"])

    parsed = parser.parse_args([])
    assert parsed.config == "foo.ini"
    assert parsed.dry_run is True

    override = parser.parse_args(["--config", "bar.ini"])
    assert override.config == "bar.ini"
    assert override.dry_run is True


def test_preset_arguments_rejects_unknown_tokens():
    parser = make_parser()

    with pytest.raises(ValueError):
        preset_arguments(parser, ["--bogus"])
