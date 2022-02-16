from dataclasses import field
from rest_framework import serializers
from .models.story import Story, Tags


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
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = [
            "id",
            "name",
            "image",
            "content",
            "create_at",
            "is_read",
            "tags",
            "is_saved",
        ]

    def get_tags(self, obj):
        return [TagSerializers(s).data for s in obj.tags_set.all()]

    def get_is_saved(self, obj):
        if obj.saved.count() >= 1:
            is_save = True
        else:
            is_save = False
        return is_save


class storyCreateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = [
            "id",
            "name",
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
    class Meta:
        model = Story
        fields = ["id", "saved", "name"]
