import re

def lambda_handler(event, context):
    if not re.match(r'^[A-Za-z_\-0-9.]+$', event['userName']):
        raise Exception("Invalid username")

    return event
