from .fields import Name, Phone, Birthday, Address, Email
from .errors import ValidationError
from .colorize import Colorize


class Record:
    """
    Stores all data about a contact:
    - Name
    - Multiple phones
    - Multiple emails
    - One birthday
    - One address
    """

    def __init__(self, name):
        """Initializes Record with a Name and empty lists for phones and emails."""
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday: Birthday | None = None
        self.address: Address | None = None
        self.emails: list[Email] = []

    # ============================
    #           PHONES
    # ============================

    def add_phone(self, number: str):
        """
        Add new phone number to contact.

        - Normalizes the number via the Phone class (removes +, spaces, brackets, etc.).
        - Checks if such a normalized number already exists in the record.
        """
        try:
            phone_obj = Phone(number)  # validation + normalization
        except ValidationError as e:
            return Colorize.error(f"ERROR! No phone number was added! {e}")

        # Compare by normalized value (phone_obj.value)
        if any(p.value == phone_obj.value for p in self.phones):
            return Colorize.error(
                f"{self.name.value}'s record already has the number: "
                f"{phone_obj.value}"
            )

        self.phones.append(phone_obj)
        return Colorize.success(
            f"{self.name.value}'s record was updated with a new number: "
            f"{phone_obj.value}"
        )

    def edit_phone(self, old_phone: str, new_phone: str):
        """
        Update existing phone number.

        - old_phone: search by normalized value (user can enter in a different format).
        - new_phone: normalize and validate before updating.
        """
        # Normalize the old number to find it in the list
        try:
            normalized_old = Phone(old_phone).value
        except ValidationError:
            # If the old number is not even valid — try to search as is
            normalized_old = old_phone

        # Find the target Phone object
        target_phone = None
        for phone in self.phones:
            if phone.value == normalized_old or phone.value == old_phone:
                target_phone = phone
                break

        if not target_phone:
            return Colorize.error(f"User {self.name.value} has no phone {old_phone}.")

        # Update with the new number (validation + normalization)
        try:
            target_phone.update(new_phone)
            return Colorize.success(
                f"{self.name.value}'s record was updated with a new number: "
                f"{target_phone.value}"
            )
        except ValidationError as e:
            return Colorize.error(f"ERROR! No phone number was changed! {e}")

    # ============================
    #            EMAILS
    # ============================

    def add_email(self, email: str):
        """Adds email if it does not already exist."""
        try:
            email_obj = Email(email)
        except ValidationError as e:
            return Colorize.error(f"ERROR! No email was added! {e}")

        if any(e.value == email_obj.value for e in self.emails):
            return Colorize.error(f"{self.name.value}'s record already has the email: {email_obj.value}")

        self.emails.append(email_obj)
        return Colorize.success(f"{self.name.value}'s record was updated with a new email: {email_obj.value}")

    def edit_email(self, old_email: str, new_email: str):
        """Changes existing email."""
        for email_obj in self.emails:
            if email_obj.value == old_email:
                try:
                    email_obj.update(new_email)
                    return Colorize.success(
                        f"{self.name.value}'s email was changed from "
                        f"{old_email} to {new_email}"
                    )
                except ValidationError as e:
                    return Colorize.error(f"ERROR! No email was changed! {e}")

        return Colorize.error(f"User {self.name.value} has no email {old_email}.")

    def remove_email(self, email: str):
        """Deletes email from record."""
        for email_obj in self.emails:
            if email_obj.value == email:
                self.emails.remove(email_obj)
                remaining = ", ".join(e.value for e in self.emails) if self.emails else "None"
                return Colorize.success(
                    f"Email '{email}' was removed from {self.name.value}'s record.\n"
                    f"Remaining emails: {remaining}"
                )

        return Colorize.error(f"{self.name.value} has no email '{email}'.")

    # ============================
    #          BIRTHDAY
    # ============================

    def add_birthday(self, birthday: str):
        """Adds or updates birthday."""
        if self.birthday is None:
            try:
                self.birthday = Birthday(birthday)
                return Colorize.success(f"Birthday {birthday} is added to {self.name.value}'s record")
            except ValidationError as e:
                return Colorize.error(f"ERROR! {e}")

        user_input = input(
            Colorize.warning(f"{self.name.value} already has a birthday.\nChange it? Y/N: ")
        )
        if user_input.lower() == "n":
            return Colorize.info("Nothing changed")

        try:
            self.birthday = Birthday(birthday)
            return Colorize.success(f"Birth date of {self.name.value} was changed to {birthday}")
        except ValidationError as e:
            return Colorize.error(f"ERROR! {e}")

    # ============================
    #           SEARCH HELPERS
    # ============================

    def matches_phone(self, phone: str) -> bool:
        """
        Compares phones using normalized value.

        User can search for number in any format:
        - 0991234567
        - 099-123-45-67
        - +380991234567
        - 380991234567

        We normalize the entered value and compare it with the already saved
        normalized numbers.
        """
        try:
            normalized = Phone(phone).value
        except ValidationError:
            # If the search number is invalid — consider no matches
            return False

        return any(p.value == normalized for p in self.phones)

    def matches_email(self, email: str) -> bool:
        return any(e.value == email for e in self.emails)

    def matches_birthday(self, date_str: str) -> bool:
        if not self.birthday:
            return False
        return str(self.birthday) == date_str

    # ============================
    #           ADDRESS
    # ============================

    def add_address(self, address: str):
        """Sets or updates address."""
        try:
            self.address = Address(address)
            return Colorize.success(f"Address '{address}' is added to {self.name.value}'s record")
        except ValidationError as e:
            return Colorize.error(f"ERROR! {e}")

    # ============================
    #            STRING VIEW
    # ============================

    def __str__(self):
        """String representation of the contact record."""
        phones_str = f", phone(s): {'; '.join(p.value for p in self.phones)}" if self.phones else ""
        emails_str = f", email(s): {'; '.join(e.value for e in self.emails)}" if self.emails else ""
        bday_str = f", birthday: {self.birthday}" if self.birthday else ""
        address_str = f", address: {self.address.value}" if self.address else ""
        return f"Contact name: {self.name.value}{phones_str}{emails_str}{bday_str}{address_str}"
