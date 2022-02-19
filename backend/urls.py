from django.urls import include
from django.urls import path

from .views import *

urlpatterns = [
    path("publish/<int:pk>/", set_publish_status, name="set-publish-status"),
    path("", StoryView.as_view(), name="story-view"),
    path(
        "save/",
        StorySavedReadAPIView.as_view(),
        name="save-view",
    ),
    path("read/", StorySavedReadAPIView.as_view(), name="read-view"),
    path("notifications/<int:pk>/", notification_send, name="read-view"),
]

urlpatterns += [
    path("", include("accounts.urls")),
]
