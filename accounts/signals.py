from django.core.mail import send_mail
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.db.models.signals import post_save, pre_save
from django.contrib.sites.shortcuts import get_current_site
from .models.user import User
from django.conf import settings


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
    email_plaintext_message = "{}?token={}".format(
        reverse("password_reset:reset-password-request"), reset_password_token.key
    )

    send_mail(
        # title:
        "Password Reset for {title}".format(title="Flow News"),
        # message:
        email_plaintext_message,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email],
    )


def update_null_to_empty_string(sender, instance, **kwargs):
    if instance.email == "null" or instance.email == None:
        instance.email = ""
    if instance.first_name == "null" or instance.first_name == None:
        instance.first_name = ""
    if instance.last_name == "null" or instance.last_name == None:
        instance.last_name = ""
    if instance.phone_number == "null" or instance.phone_number == None:
        instance.phone_number = ""
    if instance.device_id == "null" or instance.device_id == None:
        instance.device_id = ""
    if instance.device_type == "null" or instance.device_type == None:
        instance.device_type = ""


post_save.connect(update_null_to_empty_string, sender=User)
pre_save.connect(update_null_to_empty_string, sender=User)
