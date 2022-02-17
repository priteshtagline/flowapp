from bs4 import BeautifulSoup
from rest_framework import serializers

from .models.story import Story
from .models.story import Tags


class TagSerializers(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ["name"]


class issavedornot(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ["saved"]


class storyListSerializers(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = [
            "id",
            "title",
            "image",
            "content",
            "tags",
            "create_at",
            "is_read",
            "is_saved",
        ]

    def get_tags(self, obj):
        return [s.name for s in obj.tags_set.all()]

    def to_representation(self, data):
        data = super(storyListSerializers, self).to_representation(data)
        data["content"] = BeautifulSoup(data["content"], "html.parser").get_text()
        return data

    def to_representation(self, data):
        data = super(storyListSerializers, self).to_representation(data)
        data["content"] = BeautifulSoup(data["content"], "html.parser").get_text()
        return data


class storyCreateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = [
            "id",
            "title",
            "image",
            "content",
            "create_at",
            "is_read",
        ]


class isReadSerializers(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ["id", "is_read"]


class savedStorySerializer(serializers.ModelSerializer):
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = [
            "id",
            "title",
            "image",
            "content",
            "create_at",
            "is_read",
            "is_saved",
        ]

    def get_is_saved(self, obj):
        if obj.saved.count() > 0:
            is_save = True
        else:
            is_save = False
        return is_save

    def to_representation(self, data):
        data = super(savedStorySerializer, self).to_representation(data)
        data["content"] = BeautifulSoup(data["content"], "html.parser").get_text()
        return data
