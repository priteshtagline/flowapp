from django.urls import include
from django.urls import path

from .views import *

urlpatterns = [
    path("publish/<int:pk>/", set_publish_status, name="set-publish-status"),
    path("", StoryView.as_view(), name="story-view"),
    path(
        "save/<int:pk>/",
        StorySavedReadAPIView.as_view(),
        name="save-view",
    ),
    path("read/<int:pk>/", StorySavedReadAPIView.as_view(), name="read-view"),
]

urlpatterns += [
    path("", include("accounts.urls")),
]
