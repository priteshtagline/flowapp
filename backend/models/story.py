from operator import mod
from ckeditor.fields import RichTextField
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Story(models.Model):
    name = models.CharField(_("Name"), max_length=1000)
    content = RichTextField()
    is_publish = models.BooleanField(default=False)
    expiration_time = models.DateTimeField(db_index=True, null=True, blank=True)

    class Meta:
        verbose_name = _("Story")
        verbose_name_plural = _("Story")

    def __str__(self):
        return self.name


class Tags(models.Model):
    name = models.CharField(_("Tag name"), max_length=1000, null=True, blank=True)
    Story = models.ForeignKey(Story, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Tags")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.name
