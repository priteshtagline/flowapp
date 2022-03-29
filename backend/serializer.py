from dataclasses import fields
from bs4 import BeautifulSoup
from rest_framework import serializers

from .models.story import Story
from accounts.models.user import User
from .models.story import Tags


class TagSerializers(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ["name"]


class storySerializers(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = [
            "id",
            "title",
            "author",
            "image",
            "content",
            "tags",
            "read",
            "saved",
            "create_at",
            "update_at",
            "publish_at",
        ]

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags_set.all()]

    def to_representation(self, data):
        data = super(storySerializers, self).to_representation(data)
        # Rich text box html content convert into normal string data.
        data["content"] = BeautifulSoup(
            data["content"], "html.parser").get_text()
        if data["update_at"] == "null" or data["update_at"] == None:
            data["update_at"] = ""
        if data["publish_at"] == "null" or data["publish_at"] == None:
            data["publish_at"] = ""
        return data
