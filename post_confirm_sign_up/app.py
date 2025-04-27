import os
import boto3

# get db name from environment variable PLAYER_STORAGE_TABLE
table_name = os.environ['PLAYER_STORAGE_TABLE']

def lambda_handler(event, context):

    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(table_name)

    # get the user id from the event
    user_id = event['userName']

    # add to the database
    response = table.put_item(
        Item={
            'username': user_id,
            'totalCubesDropped': 0,
            'matchCount': 0,
            "achievements": []
        }
    )

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception('Error adding user to database')

    return event