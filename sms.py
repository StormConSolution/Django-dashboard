import os
from twilio.rest import Client

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

FROM = '+16194942627'

def send(body, to):
    message = client.messages.create(
        body=body,
        from_=FROM,
        to=to
    )

    print(message.sid)
