"""Module contains helper methods used by other modules in the package."""


def env_exists(env_variable: str) -> bool:
    """Validates if env variable was provided and is not an empty string.

    Args:
        env_variable: str, name of the env variable

    Returns:
        True: if env provide and not an empty string
        False: if env not provided or an empty string
    """
    if env_variable is not None and env_variable != '':
        return True
    return False


def env_as_bool(env_variable: str, default: bool = False) -> bool:
    """Casts env variable to boolean, returns default if unset."""
    if not env_exists(env_variable):
        return default
    return str(env_variable).strip().lower() in ['1', 'true', 'yes', 'on']


def env_as_int(env_variable: str, default: int) -> int:
    """Casts env variable to integer, returns default on failure."""
    if not env_exists(env_variable):
        return default
    try:
        return int(env_variable)
    except (TypeError, ValueError):
        return default


def normalize_env_value(env_variable: str,
                        strip_inline_comment: bool = False) -> str:
    """Normalizes env value by stripping spaces and optional inline comments."""
    if not env_exists(env_variable):
        return None
    normalized = str(env_variable)
    if strip_inline_comment and '#' in normalized:
        normalized = normalized.split('#', 1)[0]
    normalized = normalized.strip()
    if normalized == '':
        return None
    return normalized
