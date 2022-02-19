from django.db.models import Q
from django.shortcuts import redirect
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from fcm_django.models import FCMDevice

from backend.models.story import Story

from .models.story import Story
from .serializer import storySerializers
from accounts.models import User


def set_publish_status(request, pk):
    """Update story status."""
    Story.objects.filter(pk=pk).update(status="publish")
    return redirect("/admin/backend/story")


def str2bool(v):
    return v.lower() in ("true")


def read_or_save_story(flag, instance, request):
    if flag == "is_saved":
        flagValue = request.GET.get("is_saved", None)
        obj = instance.saved

    if flag == "is_read":
        flagValue = request.GET.get("is_read", None)
        obj = instance.read

    if flag and str2bool(flagValue):
        obj.add(request.user.id)
    elif flag and not str2bool(flagValue):
        obj.remove(request.user.id)


class StoryView(generics.ListAPIView):
    """Returns all story whose are published."""

    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = storySerializers
    queryset = Story.objects.exclude(
        Q(status="draft") | Q(status="unpublish") | Q(status="archived")
    ).order_by("-create_at")


class StorySavedReadAPIView(generics.GenericAPIView):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = storySerializers
    model = Story

    def get_object(self):
        try:
            return self.model.objects.get(pk=self.request.GET.get("story_id"))
        except:
            return None

    def post(self, request, *args, **kwargs):
        if not self.get_object():
            return Response(
                {"error": {"story_id": ["Please provide valid story id."]}}, status=400
            )
        url = request.build_absolute_uri()
        flagName = None
        if "is_saved" in url:
            flagName = "is_saved"
        if "is_read" in url:
            flagName = "is_read"
        read_or_save_story(flagName, self.get_object(), request)
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)


def notification_send(request, pk):
    all_devices = FCMDevice.objects.order_by("device_id", "-id").distinct("device_id")
    story_instance = Story.objects.get(pk=pk)

    notification_data = dict()
    notification_data["title"] = story_instance.title
    notification_data["body"] = story_instance.content if story_instance.message else ""
    notification_data["image"] = (
        story_instance.image.url if story_instance.image else ""
    )

    device_token_list = (
        all_devices.exclude(registration_id__isnull=True)
        .exclude(registration_id="null")
        .values_list("registration_id", flat=True)
    )

    for i in device_token_list:
        i.send_message(notification_data)
