#!/usr/bin/env python3
import base64
import requests
import newrelic.agent
import boto3
from botocore.exceptions import ClientError

newrelic.agent.initialize('newrelic.ini')
app = newrelic.agent.register_application()

def get_secret():

    secret_name = "platform/azuredevopstonewrelic/adopoolsstatuspat"
    region_name = "us-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            return get_secret_value_response['SecretString']
        else:
            return base64.b64decode(get_secret_value_response['SecretBinary'])

username = "" # This can be an arbitrary value or you can just let it empty
password = get_secret()
userpass = username + ":" + password
b64 = base64.b64encode(userpass.encode()).decode()
request_headers = {"Authorization" : "Basic %s" % b64}

def get_ado_pools_json_output(headers):
    url = "https://dev.azure.com/ORG/_apis/distributedtask/pools?api-version=6.0"
    response = requests.get(url, headers=headers)
    json_output = response.json()
    return json_output

def validate_ado_pools_json_output(json_output):
    if json_output['count'] > 0:
        valid_json = json_output
        return valid_json 
    else:
        print("JSON isn't valid.")

def parse_ado_pools_json_output(valid_json):
    agent_pool_array = []
    for nested in valid_json['value']:
        agent_hosted = nested['isHosted']
        agent_size = nested['size']
        agent_pool_id = nested['id']
        if (agent_hosted is False) and (agent_size > 0):
            agent_pool_array.append(agent_pool_id)
        else:
            pass
    return agent_pool_array

def get_agent_json(agent_pool_ids, headers):
    for pool_id in agent_pool_ids:
        url = f"https://dev.azure.com/ORG/_apis/distributedtask/pools/{pool_id}/agents?api-version=6.0"
        response = requests.get(url, headers=headers)
        agent_json = response.json()
        print("")
        print(f"Pool ID {pool_id} is: ")
        pool_agent_status_array = []
        for nested in agent_json['value']:
            pool_agent_status = nested['status']
            pool_agent_status_array.append(pool_agent_status)
        if pool_agent_status_array.index("online") !=-1:
            print("online")
            newrelic.agent.record_custom_event("AdoPoolsStatus", {
                "ado_pool": f"{pool_id}",
                "status": "online",
                "pool_ping": 1
            }, application=app)
        else:
            print("offline")
            newrelic.agent.record_custom_event("AdoPoolsStatus", {
                "ado_pool": f"{pool_id}",
                "status": "offline",
                "pool_ping": 0
            }, application=app)


def lambda_handler(event, context):
    json_output = get_ado_pools_json_output(request_headers)
    valid_json = validate_ado_pools_json_output(json_output)
    agent_pool_ids = parse_ado_pools_json_output(valid_json)
    try:
        get_agent_json(agent_pool_ids, request_headers)
    except ValueError:
        print("Unable to call Azure Devops")
    return "Success!"
