from django.contrib import admin
from django.utils.html import format_html

from backend.models.story import Tags, Story, PushNotification
from solo.admin import SingletonModelAdmin


class TagsAdmin(admin.StackedInline):
    model = Tags
    extra = 3
    max_num = 3


class StoryAdmin(admin.ModelAdmin):

    list_display = ["title", "status", "expiration_time"]
    inlines = [
        TagsAdmin,
    ]

    def status_button(self, obj):
        if not obj.status == "publish":
            return format_html(
                '<button><a style="color:black" href="{}">{}</a></button>',
                f"/api/publish/{obj.pk}/",
                "Publish",
            )
        else:
            return format_html(
                '<button><a style="color:black" href="{}">{}</a></button>',
                f"/api/publish/{obj.pk}/",
                "Push Notification",
            )


admin.site.register(Story, StoryAdmin)
admin.site.register(PushNotification, SingletonModelAdmin)
