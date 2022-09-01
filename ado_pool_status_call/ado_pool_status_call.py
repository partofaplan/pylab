#!/usr/bin/env python3

import requests
import base64
from newrelic import agent

username = "" # This can be an arbitrary value or you can just let it empty
password = "PAT"
userpass = username + ":" + password
b64 = base64.b64encode(userpass.encode()).decode()
headers = {"Authorization" : "Basic %s" % b64}

#def lamba_handler(event, context):
def ado_call(event, context):
    pools = range(1,100)
    try:
        for i in pools:
            poolid = i
            url = f"https://dev.azure.com/ORG/_apis/distributedtask/pools/{poolid}/agents?api-version=6.0"
            response = requests.get(url, headers=headers)
            json_output = response.json()
            if json_output['count'] > 0:
                for nested in json_output['value']:
                    status_output = nested['status']
                    test_output = f"Pool ID {poolid} is {status_output}"
                if test_output.find("online") !=-1:
                    print(f"Pool {poolid} is online")
                    agent.record_custom_event("AdoPoolStatus", {
                        "ado_pool": f"{poolid}",
                        "status": "online",
                        "pool_ping": 1
                    })
                else:
                    print(f"Pool {poolid} is offline")
                    agent.record_custom_event("AdoPoolStatus", {
                        "ado_pool": f"{poolid}",
                        "status": "offline",
                        "pool_ping": 0
                    })      
            else:
                pass
    except ValueError:
        json_output = response.text
        print(json_output)
    return "Success!"


