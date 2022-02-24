from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from solo.admin import SingletonModelAdmin

from backend.models.story import PushNotification
from backend.models.story import Story
from backend.models.story import Tags

admin.site.unregister(Group)


class TagsAdmin(admin.StackedInline):
    model = Tags
    extra = 3
    max_num = 3


class StoryAdmin(admin.ModelAdmin):
    exclude = ["saved", "read", "update_at", "notification_count"]
    list_display = ["title", "status", "status_button", "archived_deleted_tag"]
    list_filter = ("status",)
    inlines = [
        TagsAdmin,
    ]

    def status_button(self, obj):

        if not obj.status == "publish":
            Story.objects.filter(pk=obj.pk).update(notification_count="1")
            return format_html(
                '<button><a style="color:black" href="{}">{}</a></button>',
                f"/api/story/publish/{obj.pk}/",
                "Publish",
            )

        else:
            notification = Story.objects.get(id=obj.pk)
            if notification.notification_count == "1":
                return format_html(
                    '<button id="pushnotificaton"><a style="color:black" href="{}">{}</a></button>',
                    f"/api/story/notifications/{obj.pk}/",
                    "Send first notification",
                )

            elif notification.notification_count == "2":
                return format_html(
                    '<button id="pushnotificaton"><a style="color:black" href="{}">{}</a></button>',
                    f"/api/story/notifications/{obj.pk}/",
                    "Send Second notification",
                )

            else:
                return format_html("<p>Send already notification 2 times</p>")

    def archived_deleted_tag(self, obj):
        return (
            format_html(
                '<button><a style="color:black" href="{}">{}</a></button>',
                f"/api/story/deleted/{obj.pk}/",
                "Deleted",
            )
            if obj.status == "publish" or obj.status == "draft"
            else format_html("<p>Deleted with archived</p>")
        )


admin.site.register(Story, StoryAdmin)
admin.site.register(PushNotification, SingletonModelAdmin)
