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


class StorysClass(generics.ListAPIView):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = storyListSerializers
    queryset = Story.objects.exclude(
        Q(status="draft")
        | Q(status="unpublish")
        | Q(status="archived")
        | Q(create_at__gte=datetime.datetime.now())
    )


class isReadClass(generics.ListAPIView):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = isReadSerializers
    queryset = Story.objects.filter(status="publish", is_read=False)


class savedStoryClass(generics.GenericAPIView):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = savedStorySerializer
    queryset = Story.objects.all()

    def post(self, request, *args, **kwargs):
        is_saved_flag = request.GET.get("is_saved")
        instance = self.get_object()
        is_saved = instance.saved.filter(pk=request.user.id).exists()
        if is_saved:
            instance.saved.remove(request.user)
        else:
            if is_saved_flag == "True":
                instance.saved.add(request.user)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class storyCreateClass(generics.ListCreateAPIView):
    serializer_class = storyCreateSerializers
    queryset = Story.objects.all()


class storyRUD(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = storyCreateSerializers
    queryset = Story.objects.all()
