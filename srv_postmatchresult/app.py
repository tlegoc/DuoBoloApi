import json
import os

import boto3
from boto3.dynamodb.conditions import Attr

table_name = os.environ['PLAYER_STORAGE_TABLE']
matches_table_name = os.environ['MATCHES_TABLE']

milestones = [
    10,
    500,
    1000,
    200000,
    1000000,
    3141592
]


# todo use brain and do a proper achievement system with rules
def get_success_indexes(gamecount: int, cubeDropped: int):
    result = []

    result.append(0)

    for i in range(len(milestones)):
        if cubeDropped >= milestones[i]:
            result.append(i + 1)

    return result


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

    # if 'queryStringParameters' not in event or event['queryStringParameters'] is None:
    #     return {
    #         "statusCode": 400,
    #         'body': json.dumps({
    #             'error': 'Missing queryStringParameters'
    #         }),
    #         'headers': {
    #             'Access-Control-Allow-Origin': '*'
    #         }
    #     }
    #
    # if 'matchId' not in event['queryStringParameters']:
    #     return {
    #         "statusCode": 400,
    #         'body': json.dumps({
    #             'error': 'Missing matchId'
    #         }),
    #         'headers': {
    #             'Access-Control-Allow-Origin': '*'
    #         }
    #     }


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


    body = json.loads(event['body'])

    match_id = body['matchId']

    print(f"Match ID: {match_id}")

    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(table_name)
    matches_table = dynamodb.Table(matches_table_name)

    # find the match in the matches table. matchId is not the key, so we have to scan the table
    # response = matches_table.scan(
    #     FilterExpression=Attr('matchId').eq(match_id),
    #     Limit=1
    # )
    #
    # print(response)
    #
    # if 'Items' not in response:
    #     return {
    #         "statusCode": 400,
    #         'body': json.dumps({
    #             'error': 'Match not found'
    #         }),
    #         'headers': {
    #             'Access-Control-Allow-Origin': '*'
    #         }
    #     }
    #
    # if len(response['Items']) == 0:
    #     return {
    #         "statusCode": 400,
    #         'body': json.dumps({
    #             'error': 'Match not found'
    #         }),
    #         'headers': {
    #             'Access-Control-Allow-Origin': '*'
    #         }
    #     }

    try:

        # for each player, update their database entry
        for player in body['players']:
            try:
                # check if player was in the match
                # if player['playerId'] not in [p['playerId'] for p in response['Items'][0]['players']]:
                #     continue

                # update the database
                r = table.update_item(
                    Key={
                        'username': player['playerId']
                    },
                    UpdateExpression='SET totalCubesDropped = totalCubesDropped + :cubesDropped, matchCount = matchCount + :matchCount',
                    ExpressionAttributeValues={
                        ':cubesDropped': player['cubesDropped'],
                        ':matchCount': 1
                    },
                    ReturnValues='ALL_NEW'
                )

                if r['ResponseMetadata']['HTTPStatusCode'] != 200:
                    print(f'Error updating user {player['playerId']} in database')

                success_indexes = get_success_indexes(r['Attributes']['matchCount'],
                                                      r['Attributes']['totalCubesDropped'])

                # update the achievements
                r = table.update_item(
                    Key={
                        'username': player['playerId']
                    },
                    UpdateExpression='SET achievements = :achievements',
                    ExpressionAttributeValues={
                        ':achievements': success_indexes
                    }
                )

                if r['ResponseMetadata']['HTTPStatusCode'] != 200:
                    print(f'Error updating user {player['playerId']} in database')
            except KeyError:
                print(f'KeyError: {player}')

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
