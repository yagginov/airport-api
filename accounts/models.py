import re

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    def clean(self):
        super().clean()
        if not re.match(r"^[A-Za-z0-9_]{2,}$", self.username):
            from django.core.exceptions import ValidationError

            raise ValidationError(
                {
                    "username": "Username must contain only latin letters, digits, and underscores, min 2 chars, no spaces or special/cyrillic characters."
                }
            )
