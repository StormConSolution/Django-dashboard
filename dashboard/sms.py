import os

from django.conf import settings

from twilio.rest import Client

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

FROM = '+16194942627'

def send_sms(body, to):
    message = client.messages.create(
        body=body,
        from_=FROM,
        to=to
    )

    return message
