from django.db.models.signals import post_save, pre_save
from backend.models.story import Tags, Story
from datetime import datetime, timedelta


def update_null_to_empty_string_in_tags(sender, instance, **kwargs):
    if instance.name == "null" or instance.name == None:
        instance.name = ""


post_save.connect(update_null_to_empty_string_in_tags, sender=Tags)
pre_save.connect(update_null_to_empty_string_in_tags, sender=Tags)


def add_expiry_time_and_publish_time(sender, instance, **kwargs):
    if instance.status == "publish" and (
        instance.expiration_time == "null"
        or instance.expiration_time == None
        or instance.expiration_time == ""
    ):
        instance.expiration_time = datetime.now() + timedelta(days=1)
    if instance.status == "publish" and (
        instance.publish_at == "null"
        or instance.publish_at == None
        or instance.publish_at == ""
    ):
        instance.publish_at = datetime.now()


post_save.connect(add_expiry_time_and_publish_time, sender=Story)
pre_save.connect(add_expiry_time_and_publish_time, sender=Story)
