from django.db.models.signals import post_save, pre_save
from backend.models.story import Tags


def update_null_to_empty_string_in_tags(sender, instance, **kwargs):
    if instance.name == "null" or instance.name == None:
        instance.name = ""


post_save.connect(update_null_to_empty_string_in_tags, sender=Tags)
pre_save.connect(update_null_to_empty_string_in_tags, sender=Tags)
