import base64
import json
import boto3


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

    ticket_id = base64.b16encode(event['requestContext']['connectionId'].encode('utf-8')).decode('utf-8')

    client = boto3.client("gamelift")

    response = client.stop_matchmaking(
        TicketId=ticket_id
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Disconnected')
    }
