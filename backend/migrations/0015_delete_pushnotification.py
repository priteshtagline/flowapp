# Generated by Django 4.0.2 on 2022-02-25 09:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0014_story_archived_with_delete'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PushNotification',
        ),
    ]
