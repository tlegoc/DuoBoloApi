import boto3, os


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['PLAYER_STORAGE_TABLE'])

    user = user_table.get_item(Key={'username': token['userName']})

    if user['ResponseMetadata']['HTTPStatusCode'] != 200 :
        # Create user
        response = table.put_item(
            Item={
                'username': event['userName'],
                'display_name': event['userName'],
                'mail': event['request']['userAttributes']['email'],
                'challenges_done': [],
                'challenges_pending': [],
                'challenges_to_do': [],
                'picture_id': '',
                'show': True,
            }
        )

    return event