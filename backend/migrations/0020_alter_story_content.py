# Generated by Django 4.0.3 on 2022-03-28 13:18

import ckeditor.fields
import django.core.validators
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0019_alter_story_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='content',
            field=ckeditor.fields.RichTextField(validators=[django.core.validators.MaxLengthValidator(324)]),
        ),
    ]