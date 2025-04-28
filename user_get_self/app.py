import json
import os
import boto3
import jwt

PLAYER_STORAGE_TABLE_NAME = os.environ['PLAYER_STORAGE_TABLE']

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(PLAYER_STORAGE_TABLE_NAME)

    # retrieve jwt token from authorization header
    if 'headers' not in event or 'Authorization' not in event['headers']:
        return {
            "statusCode": 400,
            'body': json.dumps({
                'error': 'Missing Authorization header'
            }),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }

    token = event['headers']['Authorization'].replace('Bearer ', '')

    # decode jwt token
    payload = None
    try:
        payload = jwt.decode(token, algorithms=['RS256'], options={"verify_signature": False})
    except jwt.DecodeError:
        return {
            "statusCode": 401,
            'body': json.dumps({
                'error': 'Invalid token'
            }),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }

    # get user id from token (cognito:username)
    user_id = payload['cognito:username']

    # get user data from database
    response = table.get_item(
        Key={
            'username': user_id
        }
    )

    if 'Item' not in response:
        return {
            "statusCode": 404,
            'body': json.dumps({
                'error': 'User not found'
            }),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }

    user_data = response['Item']

    return {
        "statusCode": 200,
        'body': json.dumps({
            'username': user_data['username'],
            'achievements': [int(n) for n in user_data['achievements']],
            'matchCount': int(user_data['matchCount']),
            'totalCubesDropped': int(user_data['totalCubesDropped'])
        }),
        'headers': {
            'Access-Control-Allow-Origin': '*'
        }
    }
