import jwt
from jwt import ExpiredSignatureError, DecodeError
from jwt import PyJWKClient
import requests
import os

# Set up your Cognito pool data
COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
COGNITO_REGION = os.environ.get("COGNITO_REGION")
COGNITO_APP_CLIENT_ID = os.environ.get("COGNITO_USER_POOL_CLIENT_ID")
COGNITO_POOL_ISSUER = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"


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
    #
    # # Fetch public keys
    # public_keys = get_cognito_public_keys()
    #
    # rsa_key = {}
    # for key in public_keys:
    #     if key['kid'] == unverified_header['kid']:
    #         rsa_key = {
    #             'kty': key['kty'],
    #             'kid': key['kid'],
    #             'use': key['use'],
    #             'n': key['n'],
    #             'e': key['e']
    #         }

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


def lambda_handler(event, context):
    # Extract the token from the Authorization header
    token = event['querystring'].get('token', None)

    if not token:
        raise Exception("Unauthorized")

    try:
        # Validate the JWT token using the Cognito public key
        payload = validate_jwt(token)

        # If we reach here, the token is valid
        return {
            "principalId": payload["sub"],  # This can be any user-specific identifier
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [{
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": event["routeArn"]
                }]
            }
        }
    except Exception as e:
        print(e)
        raise Exception("Unauthorized")
