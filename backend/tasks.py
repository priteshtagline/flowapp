from celery import shared_task

from backend.models.story import Story
import datetime


@shared_task
def hello():
    story = Story.objects.filter(
        status__exact="publish", expiration_time__lt=datetime.datetime.now()
    ).update(status="archived")
