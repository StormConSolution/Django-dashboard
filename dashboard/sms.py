import os

from django.conf import settings

from twilio.rest import Client

FROM = '+16194942627'

def send_sms(body, to):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN

    try:
        client = Client(account_sid, auth_token)
    except:
        return None

    message = client.messages.create(
        body=body,
        from_=FROM,
        to=to
    )

    return message
