from colorama import Fore, Style, init


class Colorize:
    """Class for colorizing console output using colorama."""

    init()

    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Applies the specified color to the given text."""
        color_dict = {
            "error": Fore.RED,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "info": Fore.BLUE,
            "highlight": Fore.CYAN,
        }
        color_code = color_dict.get(color.lower(), Fore.RESET)
        return f"{color_code}{text}{Style.RESET_ALL}"

    # Simplified method names for easier use
    @staticmethod
    def error(message: str) -> str:
        """Applies error color to the message."""
        return Colorize.colorize(message, "error")

    @staticmethod
    def success(message: str) -> str:
        """Applies success color to the message."""
        return Colorize.colorize(message, "success")

    @staticmethod
    def warning(message: str) -> str:
        """Applies warning color to the message."""
        return Colorize.colorize(message, "warning")

    @staticmethod
    def info(message: str) -> str:
        """Applies info color to the message."""
        return Colorize.colorize(message, "info")

    @staticmethod
    def highlight(message: str) -> str:
        """Applies highlight color to the message."""
        return Colorize.colorize(message, "highlight")