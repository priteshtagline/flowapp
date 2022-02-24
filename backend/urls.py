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
    path(
        "notifications/<int:pk>/", notification_send, {"result": 0}, name="notification"
    ),
    path(
        "deleted/<int:pk>/",
        archived_deleted_tag,
        name="archived_deleted_tag",
    ),
]

urlpatterns += [
    path("saved_list/", SavedAPIView.as_view(), name="saved_list"),
]
