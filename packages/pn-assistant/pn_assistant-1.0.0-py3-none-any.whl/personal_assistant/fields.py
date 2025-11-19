from datetime import datetime
from typing import Any
import re

from .errors import ValidationError


class Field:
    """Base class for all fields: stores value and provides minimal validation."""

    def __init__(self, value):
        self.value = self.validate(value)

    def validate(self, value) -> Any:
        """Base validator: check string type, strip spaces, ensure not empty."""
        value = self.base_validate(value)
        return value

    @staticmethod
    def base_validate(value):
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")

        value = value.strip()
        if not value:
            raise ValidationError("Field cannot be empty")
        return value

    def update(self, new_value):
        """Updates field value with validation."""
        self.value = self.validate(new_value)

    def __str__(self) -> str:
        """String representation of the field."""
        return str(self.value)


# ===============================
#       SPECIFIC FIELDS
# ===============================


class Name(Field):
    """Name uses only base validation."""

    pass


class Phone(Field):
    """
    Phone with normalization for Ukrainian numbers.

    - Removes all characters except digits (spaces, parentheses, dashes, '+').
    - Accepts:
        * 10 digits starting with '0'     -> converted to format 380XXXXXXXXX
        * 12 digits starting with '380'   -> considered already normalized
    - Stores values ​​only in the format '380XXXXXXXXX'.
    """

    NON_DIGITS_PATTERN = re.compile(r"\D+")

    def validate(self, value):
        """Validates and normalizes Ukrainian phone numbers."""
        raw = self.base_validate(value)

        # 1) normalize: remove all non-digit characters
        digits = re.sub(self.NON_DIGITS_PATTERN, "", raw)

        # 2) if already in the format 380XXXXXXXXX
        if digits.startswith("380") and len(digits) == 12:
            return digits

        # 3) local format 0XXXXXXXXX -> convert to 380XXXXXXXXX
        if digits.startswith("0") and len(digits) == 10:
            return "38" + digits  # 0XXXXXXXXX -> 380XXXXXXXXX

        # 4) everything else is considered a non-Ukrainian number
        raise ValidationError(
            "Phone must be a Ukrainian number: 10 digits starting with 0 "
            "or 12 digits starting with 380"
        )


class Birthday(Field):
    """Stores birthday as datetime. Input must be DD.MM.YYYY."""

    DATE_PATTERN = re.compile(r"\d{2}\.\d{2}\.\d{4}$")

    def validate(self, value):
        """Validates birthday format and converts to datetime."""
        if not isinstance(value, str):
            raise ValidationError("Birthday must be a string")

        birthday = value.strip()

        if not self.DATE_PATTERN.match(birthday):
            raise ValidationError(f"Invalid date format: {birthday}. Use DD.MM.YYYY")

        try:
            return datetime.strptime(birthday, "%d.%m.%Y")
        except ValueError:
            raise ValidationError(f"Invalid date: {birthday}")

    def __str__(self) -> str:
        return self.value.strftime("%d.%m.%Y")


class Email(Field):
    """Simple email validator based on regex."""

    EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

    def validate(self, value):
        """Validates email format."""
        email = self.base_validate(value)
        if not self.EMAIL_PATTERN.match(email):
            raise ValidationError(f"Invalid email format: {email}")
        return email


class Address(Field):
    """
    Minimal address validation:
    - Not empty
    - Minimal length: 5
    - Allowed characters: letters, digits, comma, dot, dash, slash, space
    """

    ALLOWED_PATTERN = re.compile(r"^[A-Za-z0-9а-яА-ЯёЁіІїЇєЄ ,.\-\/]+$")

    def validate(self, value):
        """Validates address format and length."""
        address = self.base_validate(value)

        if len(address) < 5:
            raise ValidationError("Address is too short")

        if not self.ALLOWED_PATTERN.match(address):
            raise ValidationError("Address contains forbidden characters")

        return address


class Title(Field):
    """Title must be a non-empty string."""
    
    def validate(self, value):
        """Validates title as non-empty string."""
        return self.base_validate(value)


class Content(Field):
    """Content may be empty."""
    
    def validate(self, value):
        """Validates content (may be empty)."""
        return value


class Tags(Field):
    """Tags are comma-separated text, non-empty."""
    
    def validate(self, value):
        """Validates tags as comma-separated text, non-empty."""
        return self.base_validate(value)
