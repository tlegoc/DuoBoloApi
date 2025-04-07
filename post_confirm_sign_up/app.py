import os
import boto3

def lambda_handler(event, context):

    client = boto3.client('dynamodb')

    # get db name from environment variable PLAYER_STORAGE_TABLE
    table_name = os.environ['PLAYER_STORAGE_TABLE']

    # get the user id from the event
    user_id = event['userName']

    # add to the database
    response = client.put_item(
        TableName=table_name,
        Item={
            'username': {
                'S': user_id
            }
        }
    )

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception('Error adding user to database')

    return event