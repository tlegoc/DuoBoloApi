import time
from datetime import datetime, timedelta
import json
import boto3
import os
import base64

region = os.environ['REGION']
websocket_api_id = os.environ['WEBSOCKET_API_ID']
stage = os.environ['STAGE']
cluster = os.environ['CLUSTER']
task = os.environ['LAUNCH_TASK']
subnet_a = os.environ['SUBNET_A']
subnet_b = os.environ['SUBNET_B']
security_group = os.environ['SECURITY_GROUP']
matches_table = os.environ.get("MATCHES_TABLE")

def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])

    # ensure message is match succeeded
    if message['detail']['type'] != 'MatchmakingSucceeded':
        return

    tickets = message["detail"]["tickets"]
    match_id = message["detail"]["matchId"]

    print(f"Starting {task} on {cluster} for match {match_id}")

    # launch a task
    ecs = boto3.client('ecs')

    task_id = ""

    match_launched = False
    try:
        response = ecs.run_task(
            cluster=cluster,
            count=1,
            enableECSManagedTags=True,
            startedBy='mm_onmatchfound',
            taskDefinition=task,
            clientToken=match_id,
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [subnet_a, subnet_b],
                    'securityGroups': [security_group],
                    'assignPublicIp': 'ENABLED'
                }
            },
        )

        task_arn = response['tasks'][0]['taskArn']
        task_id = task_arn.split('/')[-1]
        match_launched = True
    except Exception as e:
        print(f"Error launching task {e}, cancelling tickets")

    # add match to matches table
    # match : { "Players": [ { "connection": CONNECTION_ID, "ticket": TICKET_ID } ], "TTLAttrib": CREATION_TIME_PLUS_1HOUR }

    players = []
    for ticket in tickets:
        ticket_id = ticket["ticketId"]

        connection_id = base64.b16decode(ticket_id.encode('utf-8')).decode('utf-8')
        players += [
            {
                'ConnectionId': connection_id,
                'TicketId': ticket_id
            }
        ]

    dynamo = boto3.resource('dynamodb')
    table = dynamo.Table(matches_table)

    # add match to matches table
    try:
        if match_launched:
            current_time = int(datetime.now().timestamp())
            expiration_time = int((datetime.now() + timedelta(hours=2)).timestamp())

            table.put_item(
                Item={
                    'MatchId': match_id,
                    'TaskId': task_id,
                    'CreationTime': current_time,
                    'ExpirationTime': expiration_time,  # 1 hour from now
                    'Players': players
                }
            )
    except Exception as e:
        print(f"Error adding match to table {e}")
        if match_launched:
            # cancel task
            try:
                # wait for 2 seconds
                print("Waiting for 2 seconds before stopping task")
                time.sleep(2)
                response = ecs.stop_task(
                    cluster=cluster,
                    task=task_id,
                    reason='Matchmaking failed'
                )
                print(f"Stopped task {task_id}: {response}")
            except Exception as e:
                print(f"Error stopping task {e}")

        match_launched = False

    for player in players:
        connection_id = player["ConnectionId"]

        print(f"Canceling connection {connection_id}")
        gateway = boto3.client('apigatewaymanagementapi', endpoint_url=f'https://{websocket_api_id}.execute-api.{region}.amazonaws.com/{stage}')
        try:
            if match_launched:
                gateway.post_to_connection(
                    ConnectionId=connection_id,
                    Data=json.dumps({'status': 'found'})
                )
            else:
                gateway.delete_connection(
                    ConnectionId=connection_id
                )
        except Exception as e:
            print(f"Error on ticket {connection_id}: {e}")