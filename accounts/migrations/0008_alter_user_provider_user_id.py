# Generated by Django 4.0.2 on 2022-02-24 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_user_is_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='provider_user_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
