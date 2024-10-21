import os
import json
import boto3
import logging
    
iot_twinmaker = boto3.client('iottwinmaker')
WORKSPACE_ID = os.environ['WORKSPACE_ID']
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def lambda_handler(event, context):
    logging.debug(event)
    try:
        # get the dynamic entity ID from the event
        dynamic_entity_id = event['body']['dynamic_entity_id']
        
        # new location for the entity from the triggering event
        loc_x = event['body']['loc_x']
        loc_y = event['body']['loc_y']
        rotation = event['body']['rotation_y']
            
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
                        },
                        "transform_rotation": {
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
                                    { "doubleValue": 0 },
                                    { "doubleValue": rotation },
                                    { "doubleValue": 0 }
                                ]
                            }
                        }
                    }
                }
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps('moved')
        }
    except Exception as e:
        logging.error(e)
        return {
            'statusCode': 400,
            'body': 'dynamic_entity_id not found in event'
        }
