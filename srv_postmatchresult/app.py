import json
import os

import boto3

table_name = os.environ['PLAYER_STORAGE_TABLE']
matches_table_name = os.environ['MATCHES_TABLE']

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

    if 'matchId' not in event['queryStringParameters']:
        return {
            "statusCode": 400,
            'body': json.dumps({
                'error': 'Missing matchId'
            }),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }

    match_id = event['queryStringParameters']['matchId']

    """
    {
        "matchId": "string",
        "players": [
            {
                "playerId": "username",
                "cubesDropped": 100
            }
        ]
    }
    """

    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(table_name)
    matches_table = dynamodb.Table(matches_table_name)

    # check if the match id exists
    response = matches_table.get_item(
        Key={
            'TaskId': match_id
        }
    )

    if 'Item' not in response:
        return {
            "statusCode": 400,
            'body': json.dumps({
                'error': 'Match not found'
            }),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }

    try:
        body = json.loads(event['body'])

        # for each player, update their database entry
        for player in body['players']:
            # check if player was in the match
            if player['playerId'] not in [p['PlayerId'] for p in response['Item']['Players']]:
                continue

            # update the database
            r = table.update_item(
                Key={
                    'username': player['playerId']
                },
                UpdateExpression='SET totalCubesDropped = totalCubesDropped + :cubesDropped, matchCount = matchCount + :matchCount',
                ExpressionAttributeValues={
                    ':cubesDropped': player['cubesDropped'],
                    ':matchCount': 1
                }
            )

            if r['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise Exception('Error updating user in database')
    except Exception as e:
        return {
            "statusCode": 400,
            'body': json.dumps({
                'error': str(e)
            }),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }

    return {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Origin': '*'
        }
    }
