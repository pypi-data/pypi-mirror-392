import argparse
from collections.abc import Sequence


def _find_action(
    parser: argparse.ArgumentParser, arg_name: str
) -> argparse.Action | None:
    """Helper function to find an Action object by any of its option strings."""
    for action in parser._actions:
        if arg_name in action.option_strings or arg_name == action.dest:
            return action
    return None


def remove_argument(parser: argparse.ArgumentParser, name_to_find: str):
    """
    Removes an argument from a parser, identified by an option string or dest.

    Args:
        parser: The ArgumentParser object to modify.
        name_to_find: An option string or dest of the argument to remove.

    Raises:
        ValueError: If the argument is not found in the parser.
    """
    action_to_remove = _find_action(parser, name_to_find)
    if not action_to_remove:
        raise ValueError(f"Argument '{name_to_find}' not found in the parser.")

    # Remove all associated option strings from the internal mapping.
    for option_string in action_to_remove.option_strings:
        parser._option_string_actions.pop(option_string, None)

    # Remove the action from the master _actions list.
    parser._actions.remove(action_to_remove)

    # Remove the action from any action group to keep help output in sync.
    for group in parser._action_groups:
        if action_to_remove in group._group_actions:
            group._group_actions.remove(action_to_remove)
            break

    # Remove from any mutually exclusive groups.
    for group in parser._mutually_exclusive_groups:
        if action_to_remove in group._group_actions:
            group._group_actions.remove(action_to_remove)
            break


def replace_argument_names(
    parser: argparse.ArgumentParser, name_to_find: str, new_names: list[str]
):
    """
    Replaces all option strings for a given argument with a new set of strings.

    Args:
        parser: The ArgumentParser object.
        name_to_find: An existing option string to identify the argument.
        new_names: A list of new option strings (e.g., ['-C', '--configuration']).

    Raises:
        ValueError: If the argument is not found or a new name conflicts.
    """
    action_to_modify = _find_action(parser, name_to_find)
    if not action_to_modify:
        raise ValueError(f"Argument '{name_to_find}' not found.")

    for name in new_names:
        existing_action = _find_action(parser, name)
        if existing_action and existing_action is not action_to_modify:
            raise ValueError(f"New name '{name}' conflicts with an existing argument.")

    for old_name in action_to_modify.option_strings:
        parser._option_string_actions.pop(old_name, None)

    for new_name in new_names:
        parser._option_string_actions[new_name] = action_to_modify

    action_to_modify.option_strings = new_names


def preset_arguments(
    parser: argparse.ArgumentParser, preset_args: Sequence[str]
) -> None:
    """Pre-seed the parser with values as if they appeared on the CLI."""
    if isinstance(preset_args, str):
        msg = "preset_args must be a sequence of argument tokens, not a string"
        raise TypeError(msg)

    args_list = list(preset_args)

    try:
        parsed, extras = parser.parse_known_args(args_list, argparse.Namespace())
    except SystemExit as exc:  # argparse exits on parse errors
        msg = "Failed to parse preset arguments with the provided parser"
        raise ValueError(msg) from exc

    if extras:
        extras_text = " ".join(extras)
        raise ValueError(f"Unknown preset arguments: {extras_text}")

    preset_defaults: dict[str, object] = {}
    for action in parser._actions:
        dest = action.dest
        if dest in {None, argparse.SUPPRESS} or not hasattr(parsed, dest):
            continue

        parsed_value = getattr(parsed, dest)
        default_value = parser.get_default(dest)
        if parsed_value != default_value:
            preset_defaults[dest] = parsed_value

    if preset_defaults:
        parser.set_defaults(**preset_defaults)
