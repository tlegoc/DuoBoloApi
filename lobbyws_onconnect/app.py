import json


# import requests


def lambda_handler(event, context):

    # create a matchmaking ticket

    return {
        'statusCode': 200,
        'body': json.dumps('Connected')
    }
