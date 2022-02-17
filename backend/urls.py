from django.urls import path, include
from .views import *

urlpatterns = [
    path("publish/<int:pk>/", set_publish_status, name="set-publish-status"),
    # path("api/saved/<int:pk>/", savedStory.as_view(), name=""),
    path("story/", StoryView.as_view(), name="storyview"),
    path("isread/", isReadClass.as_view(), name="isread"),
    
    # Save Unsave Story API.
    path(
        "story/<int:pk>/saved/",
        savedStoryClass.as_view(),
        name="saved",
    ),
    
    
    path("story/create/", storyCreateClass.as_view(), name="createstory"),
    path("story/<int:pk>", storyRUD.as_view(), name="rudstory"),
]

urlpatterns += [
    path("", include("accounts.urls")),
]
