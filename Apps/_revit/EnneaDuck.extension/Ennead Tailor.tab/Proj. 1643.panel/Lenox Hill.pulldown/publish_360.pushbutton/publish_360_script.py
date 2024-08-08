#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "publish_360"

try:
    import requests
    import urllib3
except:
    pass
client_id = "25N1wBFU4AaAZmWiAG5V1lLQxwj472FV"
client_secret = "APHGHGBdOTjdKuV7"


def ask_totken():

    url = 'https://website.example/id'  # Replace with your API endpoint
    request = urllib3.Request(url, headers={'Authorization': 'access_token {}'.format(client_id)})
    response = urllib3.urlopen(request)
    # Process the response

def publish_360():
    # Replace 'YOUR_ACCESS_TOKEN' with your actual access token
    access_token = "kEnG562yz5bhE9igXf2YTcZ2bu0z"
    
    
    url = "https://developer.api.autodesk.com/data/v1/projects/b.ccf84983-1c3b-4cc0-baac-73198b3364be/commands/"
    # To convert a project ID in the BIM 360 API into a project ID in the Data Management API you need to add a “b." prefix. 
    # For example, a project ID of c8b0c73d-3ae9 translates to a project ID of b.c8b0c73d-3ae9.

    
    headers = {
        "Authorization": "Bearer {}".format(access_token),
        "Content-Type": "application/vnd.api+json"
    }
    payload = {
        "jsonapi": {
            "version": "1.0"
        },
        "data": {
            "type": "commands",
            "attributes": {
                "extension": {
                    "type": "commands:autodesk.bim360:C4RPublishWithoutLinks",
                    "version": "1.0.0"
                }
            },
            "relationships": {
                "resources": {
                    "data": [{"type": "items", "id": "urn:adsk.wip:dm.file:hC6k4hndRWaeIVhIjvHu8w"}]
                }
            }
        }
    }
    response = requests.post(url, headers=headers, json=payload)

    print(response.text)

################## main code below #####################


if __name__ == "__main__":

    publish_360()






