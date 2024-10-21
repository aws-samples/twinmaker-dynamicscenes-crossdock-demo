import os
import json
import boto3
import logging
    
iot_twinmaker = boto3.client('iottwinmaker')
WORKSPACE_ID = os.environ['WORKSPACE_ID']
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def getSourceEntityId(all_entities,name):
    # get the TwinMaker entity ID from the name
    source_entity = "not found"
    for entity in all_entities['entitySummaries']:
        if entity['entityName'] == name:
            source_entity = entity['entityId']
            break
    return source_entity
    
def lambda_handler(event, context):
    logging.debug(event)
    if 'pallet' in event['body']:
        pallet_name = event['body']['pallet']
        all_entities = iot_twinmaker.list_entities(workspaceId=WORKSPACE_ID)
        source_entity_id = getSourceEntityId(all_entities,pallet_name)
        
        output = event['body']
        if source_entity_id == "not found":
            # sync from SiteWise to TwinMaker may not have occurred yet
            output['source_entity_status'] = "not_found"
            logging.debug(output)
            return {
                'statusCode': 400,
                'body': output
            }        
        else:
            output['source_entity_status'] = "found"
            output['source_entity_id'] = source_entity_id
            logging.debug(output)
            return {
                'statusCode': 200,
                'body': output
            }
    else:
        return {
            'statusCode': 400,
            'body': "Invalid request - no pallet name in request body"
        }


