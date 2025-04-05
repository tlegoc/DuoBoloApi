import re

def lambda_handler(event, context):
    if not re.match(r'^[A-Za-z_\-0-9.]+$', event['userName']):
        raise Exception("Invalid username")

    # Confirm the user
    event['response']['autoConfirmUser'] = True

    # Set the email as verified if it is in the request
    if 'email' in event['request']['userAttributes']:
        event['response']['autoVerifyEmail'] = True

    # Set the phone number as verified if it is in the request
    if 'phone_number' in event['request']['userAttributes']:
        event['response']['autoVerifyPhone'] = True

    return event
