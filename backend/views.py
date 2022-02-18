from django.db.models import Q
from django.shortcuts import redirect
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models.story import Story

from .models.story import Story
from .serializer import storySerializers


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
    queryset = Story.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except:
            return Response(
                {"error": {"story_id": ["Please provide valid story id."]}}, status=400
            )

        url = request.build_absolute_uri()
        flagName = None
        if "is_saved" in url:
            flagName = "is_saved"
        if "is_read" in url:
            flagName = "is_read"

        read_or_save_story(flagName, instance, request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
