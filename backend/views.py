import json
import logging
import os
from datetime import datetime
from datetime import timedelta
from email import message

import requests
from accounts.models.user import User
from django.contrib import messages
from django.contrib.sites.models import Site
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import response
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import strip_tags
from fcm_django.models import FCMDevice
from grpc import Status
from rest_framework import generics
from rest_framework import pagination
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models.story import Story
from backend.models.story import Tags

from .models.story import Story
from .serializer import storySerializers

logger = logging.getLogger(__name__)


def set_publish_status(request, pk):
    """Update story status."""
    stories = Story.objects.get(pk=pk)
    archived_with_deleted_tag = stories.archived_with_delete
    Story.objects.filter(pk=pk).update(
        status="publish",
        expiration_time=datetime.now() + timedelta(days=1),
        update_at=datetime.now(),
        publish_at=datetime.now(),
    )
    Story.objects.filter(pk=pk).update(
        archived_with_delete=False
    ) if archived_with_deleted_tag == True else Story.objects.filter(pk=pk).update(
        archived_with_delete=False
    )
    return redirect("/admin/backend/story")


def archived_deleted_tag(request, pk):
    Story.objects.filter(pk=pk).update(status="archived", archived_with_delete=True)

    # delete saved list while delete story
    Story.saved.through.objects.filter(story_id=pk).delete()
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


class CustomPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    page_query_param = "p"


class StoryView(generics.ListAPIView):
    """Returns all story whose are published."""

    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = storySerializers
    pagination_class = CustomPagination

    def get_object(self):
        return get_object_or_404(Story, id=self.request.query_params.get("id"))

    def get_queryset(self):
        return Story.objects.exclude(
            Q(status="draft")
            | Q(status="unpublish")
            | Q(status="archived")
            | Q(archived_with_delete=True)
            | Q(expiration_time__lt=timezone.now())
        ).order_by("-publish_at")


class SavedAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = storySerializers
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        saved_user = Story.objects.filter(
            ~Q(status="draft"),
            ~Q(status="unpublish"),
            ~Q(archived_with_delete=True),
            saved=self.request.user,
        ).order_by("-publish_at")
        serializer = storySerializers(saved_user, many=True)
        return Response(serializer.data)


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


def notification_send(request, pk, *args, **kwargs):

    story_instance = Story.objects.get(pk=pk)
    notification_inc = story_instance.notification_count
    
    Story.objects.filter(pk=pk).update(
        notification_count="2"
    ) if notification_inc == "1" or notification_inc == "null" else Story.objects.filter(
        pk=pk
    ).update(
        notification_count="3"
    )

    if int(story_instance.notification_count) < 3:
        serverToken = os.getenv("FCM_SERVER_KEY")
        if serverToken:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "key=" + serverToken,
            }
        all_devices = FCMDevice.objects.order_by("device_id", "-id").distinct(
            "device_id"
        )
        # story_instance = Story.objects.get(pk=pk)

        notification_data = dict()
        notification_data["id"] = story_instance.id
        notification_data["title"] = story_instance.title
        notification_data["body"] = (
            strip_tags(story_instance.content)
            if strip_tags(story_instance.content)
            else ""
        )
        notification_data["image"] = (
            story_instance.image.url if story_instance.image else ""
        )
        notification_data["click_action"] = "FLUTTER_NOTIFICATION_CLICK"
        device_token_list = (
            all_devices.exclude(registration_id__isnull=True)
            .exclude(registration_id="null")
            .values_list("registration_id", flat=True)
        )
        device_token_list = list(set(device_token_list))

        print("device_token_list", device_token_list)

        def divide_chunks(l, n):
            for i in range(0, len(l), n):
                yield l[i : i + n]

        deviceTokensList = list(divide_chunks(device_token_list, 900))

        if deviceTokensList:
            for fcm_token_list in deviceTokensList:
                body = {
                    "content_available": True,
                    "mutable_content": True,
                    "notification": notification_data,
                    "registration_ids": fcm_token_list,
                    "priority": "high",
                    "data": notification_data,
                }
                response = requests.post(
                    "https://fcm.googleapis.com/fcm/send",
                    headers=headers,
                    data=json.dumps(body),
                )
                print("response", response.content)

            return redirect(
                "/admin/backend/story/",
                messages.success(
                    request,
                    f"{notification_inc} Notification sent successfully",
                ),
            )
        else:
            return redirect(
                "/admin/backend/story/",
                messages.error(
                    request,
                    f"FCM token not found.",
                ),
            )
    else:
        return redirect(
            "/admin/backend/story/",
            messages.error(
                request,
                f"You can send notification only two times.",
            ),
        )
