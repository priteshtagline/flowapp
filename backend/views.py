from django.shortcuts import redirect
from backend.models.story import Story
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializer import (
    storyListSerializers,
    isReadSerializers,
    savedStorySerializer,
    storyCreateSerializers,
)
from .models.story import Story, Tags
from django.db.models import Q
from rest_framework.views import APIView
from django.http import Http404, request
from rest_framework.response import Response
import datetime


def set_publish_status(request, pk):
    """Update story status."""
    Story.objects.filter(pk=pk).update(status="publish")
    return redirect("/admin/backend/story")


class StoryView(generics.ListAPIView):
    """Returns all story whose are published."""


    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = storyListSerializers
    queryset = Story.objects.exclude(
        Q(status="draft")
        | Q(status="unpublish")
        | Q(status="archived")
    ).order_by("-create_at")



class isReadClass(generics.ListAPIView):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = isReadSerializers
    queryset = Story.objects.all()

    def post(self, request, *args, **kwargs):
        is_read_flag = request.GET.get("is_read")
        instance = self.get_object()

        instance.is_read = True if is_read_flag else False

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class savedStoryClass(generics.GenericAPIView):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = savedStorySerializer
    queryset = Story.objects.all()

    def post(self, request, *args, **kwargs):
        is_saved_flag = request.GET.get("is_saved")
        try:
            instance = self.get_object()
        except:
            return Response(
                {"error": {"story_id": ["Please provide valid story id."]}}, status=400
            )
        instance.saved.add(
            request.user.id
        ) if is_saved_flag == "true" else instance.saved.remove(request.user.id)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class storyCreateClass(generics.ListCreateAPIView):
    serializer_class = storyCreateSerializers
    queryset = Story.objects.all()


class storyRUD(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = storyCreateSerializers
    queryset = Story.objects.all()
