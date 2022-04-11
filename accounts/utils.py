import threading

from django.core.mail import EmailMessage
from fcm_django.models import FCMDevice


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data["email_subject"],
            body=data["email_body"],
            to=[data["to_email"]],
        )
        EmailThread(email).start()


def fcm_update(registration_id, device_id, user, device_type=None):
    device_query = FCMDevice.objects.filter(device_id=device_id, user__email=user.email)
    device = device_query.first()
    if device:
        device_query.update(registration_id=registration_id)
        print(
            f"FCM Update, device updated for user : {user.email} {device_id} {registration_id}"
        )
    else:
        FCMDevice.objects.create(
            device_id=device_id, registration_id=registration_id, user=user
        )
        print(
            f"FCM Update, device created for user : {user.email} {device_id} {registration_id}"
        )
