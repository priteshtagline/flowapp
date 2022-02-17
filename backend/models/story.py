from ckeditor.fields import RichTextField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from datetime import timedelta, datetime
from flowapp import settings
from django.core.validators import MaxLengthValidator


class Story(models.Model):
    title = models.CharField(_("Title"), max_length=1000)
    content = RichTextField(validators=[MaxLengthValidator(240)])
    image = models.ImageField(
        upload_to="story_image", blank=True, null=True, verbose_name="Images"
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
    is_read = models.BooleanField(_("Is Read"), default=False)
    expiration_time = models.DateTimeField(
        _("Expiration Time"), db_index=True, editable=False
    )
    saved = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="saved", blank=True
    )
    read = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="read", blank=True
    )
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _("Story")
        verbose_name_plural = _("Story")
        ordering = ["-create_at"]

    def __str__(self):
        return self.title

    def save(self):
        d = timedelta(days=1)
        if not self.id:
            self.expiration_time = datetime.now() + d
            super(Story, self).save()


class Tags(models.Model):
    name = models.CharField(_("Tag name"), max_length=1000, null=True, blank=True)
    Story = models.ForeignKey(Story, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Tags")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.name
