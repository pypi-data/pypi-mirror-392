from collections import UserDict
from datetime import datetime, date

from .record import Record
from .errors import ValidationError
from .colorize import Colorize


class AddressBook(UserDict):
    """Address book that stores multiple entries."""

    def add_record(self, record: Record):
        """Adds a new record to the address book."""
        self.data[record.name.value] = record
        return Colorize.success(f"New record for {record.name.value} was added to the book:\n{self.data}")

    def find(self, name: str) -> Record | None:
        """Finds a record by name."""
        record = self.data.get(name)
        return record if record else None

    def delete(self, name: str) -> str:
        """Deletes a record by name."""
        record = self.data.get(name)
        if not record:
            return Colorize.error(f"No contact {name} was found")
        del self.data[name]
        return Colorize.success(f"{name} deleted from contacts")

    def get_upcoming_birthdays(self, days_from_today: int) -> list[dict]:
        """
        Returns a list of contacts whose birthdays
        are in the range [today; today + days_from_today].
        """
        today = datetime.today().date()
        current_year = today.year

        upcoming_birthdays: list[dict] = []

        for record in self.data.values():
            # if there is no birthday in the entry - skip it
            if not record.birthday:
                continue

            bd = record.birthday.value.date()

            # February 29th — special case
            try:
                next_bd = bd.replace(year=current_year)
            except ValueError:
                # For the date 29.02 use 28.02
                next_bd = date(current_year, 2, 28)

            # If the birthday has already occurred this year, move to the next year
            if next_bd < today:
                try:
                    next_bd = bd.replace(year=current_year + 1)
                except ValueError:
                    next_bd = date(current_year + 1, 2, 28)

            delta_days = (next_bd - today).days

            if 0 <= delta_days <= days_from_today:
                upcoming_birthdays.append(
                    {
                        "name": record.name.value,
                        "congratulation_date": next_bd.strftime("%d.%m.%Y"),
                    }
                )

        return upcoming_birthdays

    # ===============================
    # 🔍 Search helpers
    # ===============================

    def search_by_phone(self, phone: str) -> list[Record]:
        """Search contacts by exact phone number."""
        return [rec for rec in self.data.values() if rec.matches_phone(phone)]

    def search_by_email(self, email: str) -> list[Record]:
        """Search contacts by exact email."""
        return [rec for rec in self.data.values() if rec.matches_email(email)]

    def search_by_birthday(self, date_str: str) -> list[Record]:
        """Search contacts by exact birthday date (DD.MM.YYYY)."""
        result: list[Record] = []
        for rec in self.data.values():
            try:
                if rec.matches_birthday(date_str):
                    result.append(rec)
            except ValidationError:
                # if the user entered an incorrect date in the search — just skip it
                continue
        return result
