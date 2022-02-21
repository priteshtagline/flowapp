import json
import os

import requests
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from fcm_django.models import FCMDevice

from backend.models.story import PushNotification, Story


def prepate_notification_data(instance, notification_data_image=""):
    return {
        "id": instance.id,
        "title": instance.title,
        "content": instance.content,
        "image": instance.image.url if instance.image else "",
    }


def push_notification_send(deviceTokens, notification, dataPayLoad):
    serverToken = os.getenv("FCM_SERVER_KEY")
    if serverToken:
        headers = {
            "Content-Type": "application/json",
            "Authorization": "key=" + serverToken,
        }

        def divide_chunks(l, n):
            for i in range(0, len(l), n):
                yield l[i : i + n]

        deviceTokensList = list(divide_chunks(deviceTokens, 900))
        for fcm_token_list in deviceTokensList:
            body = {
                "content_available": True,
                "mutable_content": True,
                "notification": notification,
                "registration_ids": fcm_token_list,
                "priority": "high",
                "data": dataPayLoad,
            }
            response = requests.post(
                "https://fcm.googleapis.com/fcm/send",
                headers=headers,
                data=json.dumps(body),
            )


@receiver(post_save, sender=PushNotification)
def send_custom_notification(sender, instance, **kwargs):
    all_devices = FCMDevice.objects.order_by("device_id", "-id").distinct("device_id")

    notification_data = dict()
    notification_data["title"] = instance.title
    notification_data["body"] = instance.message if instance.message else ""
    notification_data["image"] = instance.image.url if instance.image else ""

    story_data = {}
    if instance.story:
        story_data = prepate_notification_data(
            instance.story, notification_data["image"]
        )

    PushNotification.objects.update(title="", message="", image="", story="")

    device_token_list = (
        all_devices.exclude(registration_id__isnull=True)
        .exclude(registration_id="null")
        .values_list("registration_id", flat=True)
    )

    # push notification send all device.
    push_notification_send(device_token_list, notification_data, story_data)
