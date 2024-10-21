
import os
import json
import boto3
import logging
    
iot_twinmaker = boto3.client('iottwinmaker')
WORKSPACE_ID = os.environ['WORKSPACE_ID']

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def getDoorEntityId(all_entities,name):
    # get the TwinMaker entity ID from the name
    door_entity = "not found"
    for entity in all_entities['entitySummaries']:
        if entity['entityName'].startswith(name):
            #print(entity['entityId'])
            door_entity = entity['entityId']
            break
    return door_entity

def updateDoorState(door_entity_id, door_state):
    if door_state == "open":
        scale_val = 0
    elif door_state == "closed":
        scale_val = 1
    try:
        response = iot_twinmaker.update_entity(
            workspaceId=WORKSPACE_ID,
            entityId=door_entity_id,
            componentUpdates={
                "Node": {
                    "updateType": "UPDATE",
                    "propertyUpdates": {
                        "transform_scale": {
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
                                    { "doubleValue": scale_val },
                                    { "doubleValue": scale_val },
                                    { "doubleValue": scale_val }
                                ]
                            }
                        }
                    }
                }
            }
        )
    except Exception as e:
        logging.error("Error updating door state: "+str(e))
        return {
            'statusCode': 500,
            'body': 'Error updating door state'
        }

def lambda_handler(event, context):
    print(event)
    # need to determine door and change visibility
    if 'door_name' in event and 'door_state' in event:
        door_name = event['door_name']
        door_state = event['door_state']

        all_entities = iot_twinmaker.list_entities(workspaceId=WORKSPACE_ID)
        door_entity_id = getDoorEntityId(all_entities,door_name)
        logging.debug("Door entity Id: "+str(door_entity_id))

        updateDoorState(door_entity_id, door_state)

        return {
            'statusCode': 200,
            'body': json.dumps('moved')
        }
    else:
        logging.error("door_name or door_state not found in event")
        return {
            'statusCode': 400,
            'body': 'door_name or door_state not found in event'
        }