import json
import jwt
from jwt import ExpiredSignatureError, DecodeError
from jwt import PyJWKClient
import requests
import os
import base64
import boto3

# Set up your Cognito pool data
COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
COGNITO_REGION = os.environ.get("COGNITO_REGION")
COGNITO_APP_CLIENT_ID = os.environ.get("COGNITO_USER_POOL_CLIENT_ID")
COGNITO_POOL_ISSUER = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
PLAYER_STORAGE_TABLE_NAME = os.environ.get("PLAYER_STORAGE_TABLE")

# Fetch Cognito Pool public keys dynamically (public keys used to validate JWT)
def get_cognito_public_keys():
    url = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['keys']
    else:
        raise Exception("Unable to fetch Cognito public keys")


# Validate JWT token
def validate_jwt(token):
    unverified_header = jwt.get_unverified_header(token)
    if unverified_header is None or 'kid' not in unverified_header:
        raise Exception("Authorization malformed")

    url = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    jwks_client = PyJWKClient(url, headers=unverified_header)
    rsa_key = jwks_client.get_signing_key_from_jwt(token)

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=['RS256'],
                audience=COGNITO_APP_CLIENT_ID,
                issuer=COGNITO_POOL_ISSUER
            )
            return payload
        except ExpiredSignatureError:
            raise Exception("Token is expired")
        except DecodeError:
            raise Exception("Unable to decode token")
    else:
        raise Exception("Unable to find appropriate key")


MATCHMAKING_CONFIG_NAME = os.environ.get("MATCHMAKING_CONFIG_NAME")


def lambda_handler(event, context):
    # Extract the token from the Authorization header
    if "queryStringParameters" not in event:
        return {
            'statusCode': 400,
            'body': json.dumps('Unauthorized')
        }

    token = event['queryStringParameters'].get('token', None)

    if not token:
        return {
            'statusCode': 400,
            'body': json.dumps('Connected')
        }

    try:
        # Validate the JWT token using the Cognito public key
        payload = validate_jwt(token)

        # If we reach here, the token is valid
        client = boto3.client('gamelift')

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(PLAYER_STORAGE_TABLE_NAME)

        # Check if the user exists in the database
        response = table.get_item(
            Key={
                'username': payload['cognito:username']
            }
        )

        print(response)

        if 'Item' not in response:
            return {
                'statusCode': 401,
                'body': json.dumps('Unauthorized')
            }

        user_data = response['Item']

        # Get mmr (cubes dropped / matches played)
        mmr = user_data['totalCubesDropped'] / user_data['matchCount'] if user_data['matchCount'] > 0 else 0

        ticket_id = base64.b16encode(event['requestContext']['connectionId'].encode('utf-8')).decode('utf-8')
        response = client.start_matchmaking(
            TicketId=ticket_id,
            ConfigurationName=MATCHMAKING_CONFIG_NAME,
            Players=[
                {
                    'PlayerId': payload['cognito:username'],
                    'PlayerAttributes': {
                        'skill': {
                            'N': int(mmr) # TODO RETRIEVE FROM DB
                        }
                    }
                    # 'Team': 'red'
                },
            ]
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return {
                'statusCode': 500,
                'body': json.dumps('Failed to start matchmaking')
            }

        # ticket = response['MatchmakingTicket']
        # # remove StartTime and EndTime from the ticket
        # ticket.pop('StartTime', None)
        # ticket.pop('EndTime', None)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Connected',
                'user': payload['cognito:username']#,
                # 'matchmaking_ticket': ticket
            })
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 401,
            'body': json.dumps('Unauthorized')
        }

