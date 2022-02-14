from ckeditor.fields import RichTextField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from datetime import date, timedelta


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

    def save(self, *args, **kwargs):
        # MANIPULATING DATETIME
        today_date = date.today()
        # as said earlier it takes argument as day by default
        expiry_time = timedelta(1)
        self.expiration_time = today_date + expiry_time
        super(Story, self).save(*args, **kwargs)


class Tags(models.Model):
    name = models.CharField(_("Tag name"), max_length=1000, null=True, blank=True)
    Story = models.ForeignKey(Story, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Tags")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.name
