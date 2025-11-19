from warnings import warn


def warn_deprecated(old_name, new_name, removal_version=None):
    msg = f"'{old_name}' is deprecated, use '{new_name}' instead."
    if removal_version:
        msg += f" It will be removed in version {removal_version}."
    warn(
        msg,
        FutureWarning,
        stacklevel=3,
    )
