from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class LowercaseEmailField(models.EmailField):
    """
    A custom EmailField that converts email addresses to lowercase.
    """

    def get_prep_value(self, value: str) -> str:
        """Convert email address to lowercase."""
        return value.lower()


class Team(models.Model):
    """ Team model. """

    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teams")

    @property
    def members_count(self) -> int:
        """ Returns the number of members in the team. """
        return self.members.count()

    def __str__(self) -> str:
        """ Returns a string representation of the team. """
        return f'id={self.id}, {self.name}, owner={self.owner}'


class Member(models.Model):
    """ Member model. """

    email = LowercaseEmailField(blank=False, null=False)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)

    team = models.ForeignKey(Team, on_delete=models.SET_NULL, related_name="members", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="members")

    @property
    def full_name(self) -> str:
        """ Returns the full name of the member. """
        return f"{self.first_name} {self.last_name}".strip()

    @full_name.setter
    def full_name(self, name: str) -> None:
        """ Sets the full name of the member. """
        if not name:
            raise ValueError("Full name cannot be empty.")

        name_parts = name.rsplit(" ", 1)
        if len(name_parts) == 2:
            self.first_name, self.last_name = name_parts
        else:
            self.first_name = name.strip()
            self.last_name = ""

    def __str__(self) -> str:
        """ Returns a string representation of the member. """
        return f'id={self.id}, {self.full_name} ({self.email})'
