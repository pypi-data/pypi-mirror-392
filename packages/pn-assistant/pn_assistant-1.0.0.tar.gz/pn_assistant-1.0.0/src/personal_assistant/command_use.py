from enum import Enum


class Command_Use(Enum):
    """Enum class to hold all command usage strings in one place."""

    # ---------------- General ----------------
    HELLO = "hello"
    CLOSE = "close"
    EXIT = "exit"

    # ---------------- Phone ----------------
    ADD = "add <name> <phone>"
    CHANGE = "change <name> <old-phone> <new-phone>"

    # ---------------- Contact ----------------
    DELETE = "delete <name>"

    # ---------------- Emails ----------------
    ADD_EMAIL = "add-email <name> <email>"
    CHANGE_EMAIL = "change-email <name> <old-email> <new-email>"
    DELETE_EMAIL = "delete-email <name> <email>"

    # ---------------- Birthdays ----------------
    ADD_BIRTHDAY = "add-birthday <name> <birthday>"
    BIRTHDAYS = "birthdays[ <days-from-today>]"

    # ---------------- Address ----------------
    ADD_ADDRESS = "add-address <name> <address>"

    # ---------------- Show Contact's Info ----------------
    PHONE = "phone <name>"
    BIRTHDAY = "birthday <name>"
    EMAIL = "email <name>"
    CONTACT = "contact <name>"
    ALL = "all"

    # ---------------- Notes ----------------
    ADD_NOTE = "add-note"
    FIND_NOTE_BY_TITLE = "find-note-by-title"
    DELETE_NOTE = "delete-note"
    CHANGE_NOTE = "change-note"
    FIND_NOTE_BY_TAG = "find-note-by-tag"
    ALL_NOTES = "all-notes"


# Commands list for autosuggest and "Did you mean..?"
command_list = [
    "hello",
    "exit",
    "close",
    "help",
    "add",
    "change",
    "delete",
    "phone",
    "email",
    "birthday",
    "contact",
    "all",
    "add-address",
    "add-email",
    "change-email",
    "delete-email",
    "add-birthday",
    "birthdays",
    "search",
    "add-note",
    "find-note-by-title",
    "delete-note",
    "change-note",
    "find-note-by-tag",
    "all-notes",
]
