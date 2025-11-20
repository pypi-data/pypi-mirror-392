import boto3
from django.core.mail import send_mail
from django.conf import settings

class EasyNotify:
    def __init__(self, mode="sns"):
        self.mode = mode
        self.sns_client = boto3.client("sns") if mode == "sns" else None

    def send(self, subject, message, target=None, emails=None):
        if self.mode == "sns":
            if not target:
                raise ValueError("SNS mode requires a 'target' SNS Topic ARN")
            self.sns_client.publish(
                TopicArn=target,
                Message=message,
                Subject=subject,
            )

        elif self.mode == "email":
            if not emails:
                raise ValueError("Email mode requires a list of emails")
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                emails,
                fail_silently=False,
            )

        else:
            print(f"[Console] {subject}: {message}")
