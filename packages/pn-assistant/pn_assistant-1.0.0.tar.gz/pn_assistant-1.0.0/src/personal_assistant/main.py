import difflib
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion


from personal_assistant import (
    Command_Use,
    load_data,
    save_data,
    parse_input,
    add_contact,
    change_contact,
    delete_contact,
    show_phone,
    show_email,
    show_contact,
    show_all,
    add_address,
    add_email,
    change_email,
    delete_email,
    add_birthday,
    show_birthday,
    birthdays,
    add_note,
    find_note_by_title,
    delete_note,
    change_note,
    find_note_by_tag,
    show_all_notes,
    search_contacts,
    show_help,
)
from personal_assistant.command_use import command_list
from personal_assistant.colorize import Colorize


class AutoSuggestFromList(AutoSuggest):
    """Auto-suggestion class that suggests commands from a predefined list."""

    def __init__(self, options):
        """Initializes the auto-suggest with a list of options."""
        self.options = sorted(options)

    def get_suggestion(self, buffer, document):
        """Returns a suggestion based on the current input."""
        text = document.text_before_cursor.strip()

        # If no text is entered, return None
        if not text:
            return None

        # Search for the first command that starts with the entered text
        for option in self.options:
            if option.startswith(text.lower()):
                return Suggestion(option[len(text) :])

        return None


def print_main_menu() -> None:
    """
    Displays the main menu with available commands.
    Uses the Enum Command_Use to keep all commands in one place.
    Only shown once — at program startup.
    """

    print("\n=== MAIN MENU ===")
    print("Available commands:")
    for cmd in Command_Use:
        print(f" - {cmd.value}")
    print("=================\n")


def main():
    """Main function to run the personal assistant bot."""
    
    # loading contact and note data
    book, notes = load_data()

    print(Colorize.highlight("Welcome to the assistant bot!"))
    # showing the main menu only at startup
    print_main_menu()

    # input session with command auto-suggestion
    session = PromptSession(auto_suggest=AutoSuggestFromList(command_list))

    while True:
        try:
            # reading command from the user
            user_input = session.prompt("Enter a command: ")
            # parsing command and arguments
            command, args = parse_input(user_input)

            if not command:
                continue

            match command:

                case "close" | "exit":
                    print((Colorize.highlight("Good bye!")))
                    save_data(book, notes)
                    break

                case "hello":
                    print(Colorize.highlight("How can I help you?"))

                case "help":
                    # displaying help for available commands
                    print(show_help())

                case "add":
                    print(add_contact(args, book))

                case "change":
                    print(change_contact(args, book))

                case "delete":
                    print(delete_contact(args, book))

                case "phone":
                    print(show_phone(args, book))

                case "email":
                    print(show_email(args, book))

                case "birthday":
                    print(show_birthday(args, book))

                case "contact":
                    print(show_contact(args, book))

                case "all":
                    print(show_all(book))

                case "add-address":
                    print(add_address(args, book))

                case "add-email":
                    print(add_email(args, book))

                case "change-email":
                    print(change_email(args, book))

                case "delete-email":
                    print(delete_email(args, book))

                case "add-birthday":
                    print(add_birthday(args, book))

                case "birthdays":
                    print(birthdays(args, book))

                case "search":
                    # search by phone, email, birthday
                    print(search_contacts(args, book))

                case "add-note":
                    print(add_note(notes))

                case "find-note-by-title":
                    print(find_note_by_title(notes))

                case "delete-note":
                    print(delete_note(notes))

                case "change-note":
                    print(change_note(notes))

                case "find-note-by-tag":
                    print(find_note_by_tag(notes))

                case "all-notes":
                    print(show_all_notes(notes))

                case _:
                    # Searching for the most similar command
                    matches = difflib.get_close_matches(
                        command, command_list, n=1, cutoff=0.6
                    )

                    if matches:
                        print(
                            Colorize.warning(
                                f"Invalid command. Did you mean '{matches[0]}'?"
                            )
                        )
                    else:
                        print(
                            Colorize.error(
                                "Invalid command. Type 'help' to see all commands."
                            )
                        )

        except KeyboardInterrupt:
            # Correctly handle Ctrl+C
            print(Colorize.highlight("Good bye!"))
            save_data(book, notes)
            break
        except ValueError:
            # parse_input returned something incorrect — just skip and wait for the next input
            continue


if __name__ == "__main__":
    main()
