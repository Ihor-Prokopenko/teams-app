from django.db import models
from django.contrib.auth.models import AbstractUser


class LowercaseEmailField(models.EmailField):
    """
    A custom EmailField that converts email addresses to lowercase.
    """

    def get_prep_value(self, value: str) -> str:
        """Convert email address to lowercase."""
        return value.lower()


class User(AbstractUser):
    """
    A custom User model that uses lowercase email addresses.
    """

    email = LowercaseEmailField(unique=True, blank=False, null=False)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @full_name.setter
    def full_name(self, name) -> None:
        """ Sets the full name of the user. """
        if not name:
            raise ValueError("Full name cannot be empty.")

        name_parts = name.rsplit(" ", 1)
        if len(name_parts) == 2:
            self.first_name, self.last_name = name_parts
        else:
            self.first_name = name.strip()
            self.last_name = ""

    def save(self, *args, **kwargs) -> None:
        """ Override the save method to set the email as the username. """
        self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Represent the User model as a string."""
        return f"{self.email}"
