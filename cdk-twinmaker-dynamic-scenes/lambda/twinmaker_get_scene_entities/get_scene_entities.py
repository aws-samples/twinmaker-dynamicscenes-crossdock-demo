
import os
import json
import boto3
import logging
    
iot_twinmaker = boto3.client('iottwinmaker')
WORKSPACE_ID = os.environ['WORKSPACE_ID']
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def get_entity_id(parent):
    try:
        response = iot_twinmaker.list_entities(
            workspaceId = WORKSPACE_ID,
            filters = [{ 'parentEntityId' : parent }]
            )
        return response['entitySummaries'][0]['entityId']
    except:
        return None

def lambda_handler(event, context):
    logging.debug(event)
    output = event['body']
    try:
        # need to get the scene entity Id
        scene_entity = get_entity_id('SCENES_EntityId')
        logging.debug(str(scene_entity))

        output['scene_parent'] = scene_entity

        return {
            'statusCode': 200,
            'body': output
        } 
    except Exception as e:
        logging.error(e)
        return {
            'statusCode': 500,
            'body': "error getting parent entities from TwinMaker"
        }