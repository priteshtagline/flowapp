from django.contrib import admin
from django.utils.html import format_html

from .models import *


class TagsAdmin(admin.TabularInline):
    model = Tags
    extra = 1


class StoryAdmin(admin.ModelAdmin):
    exclude = ("expiration_time",)

    list_display = ["name", "status","expiration_time"]
    inlines = [
        TagsAdmin,
    ]

    def status(self, obj):
        if not obj.is_publish:
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
