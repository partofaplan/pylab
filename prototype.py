#!/usr/bin/env python3
from ctypes import Array
from multiprocessing import pool
import requests
import base64
import json

# This is all the necessary info for the API
username = "" # This can be an arbitrary value or you can just let it empty
password = "z3y733uqdskb5zuyjk5u6jt3mnuo6ichso5s6da662yxy4cbavba"
userpass = username + ":" + password
b64 = base64.b64encode(userpass.encode()).decode()
headers = {"Authorization" : "Basic %s" % b64}

# Api call piece
def ado_call():
    global json_output
    url = f"https://dev.azure.com/mindbody/_apis/distributedtask/pools?api-version=6.0"
    response = requests.get(url, headers=headers)
    json_output = response.json()
ado_call()

def ado_json_validator():
    global valid_json
    if json_output['count'] > 0:
        valid_json = json_output
        return valid_json 
    else:
        print("JSON isn't valid.")
ado_json_validator()

def ado_json_parser():
    global agent_pool_id
    global agent_pool_array
    agent_pool_array = []
    for nested in valid_json['value']:
        agent_hosted = nested['isHosted']
        agent_size = nested['size']
        agent_pool_id = nested['id']
        if (agent_hosted == False) and (agent_size > 0):
            agent_pool_array.append(agent_pool_id)
        else:
            pass
ado_json_parser()

def lambda_handler():
    global agent_json
    try:
        for pool_id in agent_pool_array:
            url = f"https://dev.azure.com/mindbody/_apis/distributedtask/pools/{pool_id}/agents?api-version=6.0"
            response = requests.get(url, headers=headers)
            agent_json = response.json()
            print("")
            print(f"Pool ID {pool_id} is: ")
            pool_agent_status = []
            for nested in agent_json['value']:
                pool_agent_status = (nested['status'])
            if pool_agent_status.find("online") !=-1:
                print("online")
                agent.record_custom_event("AdoPoolsStatus", {
                    "ado_pool": f"{pool_id}",
                    "status": "online",
                    "pool_ping": 1
                })
            else:
                print("offline")
                agent.record_custom_event("AdoPoolsStatus", {
                    "ado_pool": f"{pool_id}",
                    "status": "offline",
                    "pool_ping": 0
                })
    except ValueError:
        json_output = response.text
        print(json_output)
    return "Success!"            
lambda_handler()


# Lambda handler piece
# def lambda_handler(event, context):
#     try:
#         #Check to see if there are even any agents in this pool ID
#         if json_output['count'] > 0:
#             #If it comes back with JSON count over 0 then it looks for the nested JSON outputs in "Value"
#             for nested in json_output['value']:
#                 status_output = nested['status']
#                 test_output = f"Pool ID {poolid} is {status_output}"
#             #Checks test_output value to see if there's an output   
#             if test_output.find("online") !=-1:
#                 print(f"Pool {poolid} is online")
#                 agent.record_custom_event("AdoPoolStatus", {
#                     "ado_pool": f"{poolid}",
#                     "status": "online",
#                     "pool_ping": 1
#                 })
#             else:
#                 print(f"Pool {poolid} is offline")
#                 agent.record_custom_event("AdoPoolStatus", {
#                     "ado_pool": f"{poolid}",
#                     "status": "offline",
#                     "pool_ping": 0
#                 })      
#         # If there's no count then there's no JSON output. This is too pass the pool.
#         else:
#             pass
#     except ValueError:
#         json_output = response.text
#         print(json_output)
#     return "Success!"


