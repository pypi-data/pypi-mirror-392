def mask_password(password: str) -> str:
    """Mask the password for logging purposes.

    Args:
        password (str): The original password.
    Returns:
        str: The masked password.
    """
    if not password:
        return ""
    if len(password) <= 2:
        return "*" * len(password)
    return password[0] + "*" * (len(password) - 2) + password[-1]
