#!/usr/bin/env python3

import requests
import base64

def ado_call():
    pools = [9, 54, 90, 95]
    username = "" # This can be an arbitrary value or you can just let it empty
    password = "INSERT PAT HERE"
    userpass = username + ":" + password
    b64 = base64.b64encode(userpass.encode()).decode()
    headers = {"Authorization" : "Basic %s" % b64}
    try:
        for i in pools:
            poolid = i
            url = f"https://dev.azure.com/mindbody/_apis/distributedtask/pools/{poolid}/agents?api-version=6.0"
            response = requests.get(url, headers=headers)
            json_output = response.json()
            if json_output['count'] > 0:
                for nested in json_output['value']:
                    status_output = nested['status']
                    test_output = f"Pool {poolid} is {status_output}"
                if test_output.find("online") !=-1:
                    print(f"Pool {poolid} is online")
                else:
                    print(f"Pool {poolid} is offline")      
            else:
                print(f"Pool {poolid} has no agents")
    except ValueError:
        json_output = response.text
        print(json_output)
ado_call()

