import json
import boto3
import os
import base64

region = os.environ['REGION']
websocket_api_id = os.environ['WEBSOCKET_API_ID']
stage = os.environ['STAGE']

def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])

    # ensure message is match succeeded
    if message['detail']['type'] not in ['MatchmakingTimedOut', 'MatchmakingFailed']:
        return

    # cancel all websocket connections. Their id is the ticket id

    tickets = message["detail"]["tickets"]

    for ticket in tickets:
        ticket_id = ticket["ticketId"]

        connection_id = base64.b16decode(ticket_id.encode('utf-8')).decode('utf-8')
        print(f"Canceling connection {connection_id}")
        client = boto3.client('apigatewaymanagementapi', endpoint_url=f'https://{websocket_api_id}.execute-api.{region}.amazonaws.com/{stage}')
        try:
            # client.post_to_connection(
            #     ConnectionId=connection_id,
            #     Data=json.dumps({'status': 'found', 'event': message})
            # )
            client.delete_connection(
                ConnectionId=connection_id
            )
        except Exception as e:
            print(f"Error canceling ticket {connection_id}: {e}")