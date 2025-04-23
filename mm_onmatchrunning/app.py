import json
import boto3
import os

matches_table = os.environ['MATCHES_TABLE']
region = os.environ['REGION']
websocket_api_id = os.environ['WEBSOCKET_API_ID']
stage = os.environ['STAGE']

def lambda_handler(event, context):
    # receives an aws event bridge event for a fargate task running

    # get task ip
    task_arn = event['detail']['taskArn']

    # get task id
    task_id = task_arn.split('/')[-1]
    print(f"Task ID: {task_id}")

    # get task ip
    ecs = boto3.client('ecs')
    response = ecs.describe_tasks(
        cluster=os.environ['CLUSTER'],
        tasks=[task_id]
    )
    task = response['tasks'][0]
    eni = task['attachments'][0]['details'][1]['value']

    ec2 = boto3.client('ec2')

    response = ec2.describe_network_interfaces(
        NetworkInterfaceIds=[eni]
    )

    interface = response['NetworkInterfaces'][0]
    ip_address = interface['Association']['PublicIp']

    # get player connections
    dynamodb = boto3.client('dynamodb')

    response = dynamodb.get_item(
        TableName=matches_table,
        Key={
            'TaskId': {
                'S': task_id
            }
        }
    )

    # for each players in Players
    players = response['Item']['Players']['L']

    gateway = boto3.client('apigatewaymanagementapi', endpoint_url=f"https://{websocket_api_id}.execute-api.{region}.amazonaws.com/{stage}")

    for player in players:
        try:
            connection_id = player['M']['ConnectionId']['S']

            # send message to player
            response = gateway.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps({
                    'status': 'server_started',
                    'ip': ip_address
                })
            )
            print(f"Message sent to player {connection_id}: {response}")
        except Exception as e:
            print(f"Error sending message to player: {e}")
