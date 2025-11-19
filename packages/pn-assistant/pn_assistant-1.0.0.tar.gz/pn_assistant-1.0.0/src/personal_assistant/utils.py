from .command_use import Command_Use  # твій Enum
from .errors import ValidationError
from .colorize import Colorize


def input_error(func):
    """Decorator for handling input errors and providing usage messages."""
    usage_messages = {
        # General
        "HELLO": Colorize.warning(f"Usage: {Command_Use.HELLO.value}"),
        "CLOSE": Colorize.warning(f"Usage: {Command_Use.CLOSE.value}"),
        "EXIT": Colorize.warning(f"Usage: {Command_Use.EXIT.value}"),
        # Phone
        "add_contact": Colorize.warning(f"Usage: {Command_Use.ADD.value}"),
        "change_contact": Colorize.warning(f"Usage: {Command_Use.CHANGE.value}"),
        "delete_contact": Colorize.warning(f"Usage: {Command_Use.DELETE.value}"),
        "show_phone": Colorize.warning(f"Usage: {Command_Use.PHONE.value}"),
        # Emails
        "add_email": Colorize.warning(f"Usage: {Command_Use.ADD_EMAIL.value}"),
        "change_email": Colorize.warning(f"Usage: {Command_Use.CHANGE_EMAIL.value}"),
        "delete_email": Colorize.warning(f"Usage: {Command_Use.DELETE_EMAIL.value}"),
        "show_email": Colorize.warning(f"Usage: {Command_Use.EMAIL.value}"),
        # Birthdays
        "add_birthday": Colorize.warning(f"Usage: {Command_Use.ADD_BIRTHDAY.value}"),
        "birthdays": Colorize.warning(f"Usage: {Command_Use.BIRTHDAYS.value}"),
        "show_birthday": Colorize.warning(f"Usage: {Command_Use.BIRTHDAY.value}"),
        # Address
        "add_address": Colorize.warning(f"Usage: {Command_Use.ADD_ADDRESS.value}"),
        # Show Contact
        "show_contact": Colorize.warning(f"Usage: {Command_Use.CONTACT.value}"),
        "show_all": Colorize.warning(f"Usage: {Command_Use.ALL.value}"),
        # Notes
        "add_note": Colorize.warning(f"Usage: {Command_Use.ADD_NOTE.value}"),
        "find_note_by_title": Colorize.warning(f"Usage: {Command_Use.FIND_NOTE_BY_TITLE.value}"),
        "delete_note": Colorize.warning(f"Usage: {Command_Use.DELETE_NOTE.value}"),
        "change_note": Colorize.warning(f"Usage: {Command_Use.CHANGE_NOTE.value}"),
        "find_note_by_tag": Colorize.warning(f"Usage: {Command_Use.FIND_NOTE_BY_TAG.value}"),
        "show_all_notes": Colorize.warning(f"Usage: {Command_Use.ALL_NOTES.value}"),
    }

    def inner(*args, **kwargs):
        """Inner function to wrap the original function with error handling."""
        try:
            return func(*args, **kwargs)

        except ValidationError as e:
            return Colorize.error(f"Validation Error: {e.message}")

        except IndexError:
            return usage_messages.get(func.__name__, Colorize.error("Error: missing arguments"))

        except ValueError:
            return usage_messages.get(func.__name__, Colorize.error("Error: invalid value"))

        except Exception as e:
            return Colorize.error(f"Unexpected Error: {str(e)}")

    return inner
