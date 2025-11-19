def parse_input(user_input: str):
    """
    Parses user input:
    - returns the command name (cmd)
    - and a list of arguments (args: list[str])
    """
    user_input = user_input.strip()
    if not user_input:
        return "", []

    parts = user_input.split()
    cmd = parts[0].strip().lower()
    args = parts[1:]

    return cmd, args



