import os
import json
import boto3
import logging
    
iot_twinmaker = boto3.client('iottwinmaker')
WORKSPACE_ID = os.environ['WORKSPACE_ID']

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def update_entity(dynamic_entity_id,loc_x,loc_y):
    response = iot_twinmaker.update_entity(
        workspaceId=WORKSPACE_ID,
        entityId=dynamic_entity_id,
        componentUpdates={
            "Node": {
                "updateType": "UPDATE",
                "propertyUpdates": {
                    "transform_position": {
                        "definition": {
                            "dataType": {
                                "type": "LIST",
                                "nestedType": {
                                    "type": "DOUBLE"
                                }
                            }
                        },
                        "value": {
                            "listValue" : [
                                { "doubleValue": loc_x },
                                { "doubleValue": 2 },
                                { "doubleValue": loc_y }
                            ]
                        }
                    }
                }
            }
        }
    )


def lambda_handler(event, context):
    logging.debug(event)
    if 'dynamic_entity_id' in event['body']:
        dynamic_entity_id = event['body']['dynamic_entity_id']
        tag_entity_id = event['body']['tag_entity_id']
        
        # new location for the entity from the triggering event
        loc_x = event['body']['loc_x']
        loc_y = event['body']['loc_y']

        update_entity(dynamic_entity_id,loc_x,loc_y)
        update_entity(tag_entity_id, loc_x, loc_y)

        return {
            'statusCode': 200,
            'body': json.dumps('moved')
        }
    else:
        return {
            'statusCode': 400,
            'body': 'dynamic_entity_id not found in event'
        }
