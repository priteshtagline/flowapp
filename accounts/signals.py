from django.db.models.signals import post_save, pre_save
from .models.user import User


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
