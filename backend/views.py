from django.shortcuts import redirect
from .models import Story
from django.urls import path, reverse_lazy


def set_publish_status(request, pk):
    """Update story status."""
    Story.objects.filter(pk=pk).update(is_publish=True)
    return redirect("/admin/backend/story")
