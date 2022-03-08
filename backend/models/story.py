from ckeditor.fields import RichTextField
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from flowapp import settings


class Story(models.Model):
    title = models.CharField(
        _("Title"), max_length=128, validators=[MaxLengthValidator(128)]
    )
    content = RichTextField(validators=[MaxLengthValidator(384)])
    image = models.ImageField(
        upload_to="story_image",
        verbose_name="Images",
    )
    author = models.CharField(
        _("Author"),
        max_length=255,
    )
    status_choise = [
        ("publish", "publish"),
        ("unpublish", "unpublish"),
        ("draft", "draft"),
        ("archived", "archived"),
    ]
    status = models.CharField(
        _("Status"), choices=status_choise, default="draft", max_length=150
    )
    expiration_time = models.DateTimeField(
        _("Expiration Time"), db_index=True, editable=False, null=True, blank=True
    )
    saved = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="saved",
        blank=True,
    )
    read = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="read",
        blank=True,
    )
    notification_count = models.CharField(
        _("Notification_count"), default=1, null=True, blank=True, max_length=2
    )
    create_at = models.DateTimeField(auto_now_add=True, editable=False)
    update_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    publish_at = models.DateTimeField(null=True, blank=True)
    archived_with_delete = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Story")
        verbose_name_plural = _("Story")
        ordering = ["-publish_at"]

    def __str__(self):
        return self.title


class Tags(models.Model):
    name = models.CharField(_("Tag name"), max_length=1000, null=False, default="#")
    Story = models.ForeignKey(Story, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Tags")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.name
