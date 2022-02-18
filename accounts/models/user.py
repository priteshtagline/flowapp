from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..models import UserManager


class User(AbstractUser):
    """User model."""

    username = None
    first_name = models.CharField(_("First Name"), max_length=255)
    last_name = models.CharField(_("Last Name"), max_length=255)
    email = models.EmailField(_("Email Address"), unique=True)
    dob = models.DateField(blank=True, null=True)
    phone_number = models.CharField(
        blank=True,
        null=True,
        help_text="(e.g +918457221548, +33123456789)",
        max_length=12,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
