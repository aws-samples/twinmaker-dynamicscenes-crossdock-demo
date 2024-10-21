import os
import json
import boto3
import logging
    
sw_client = boto3.client('iotsitewise')
tm_client = boto3.client('iottwinmaker')
ASSET_MODEL_NAME = os.environ['ASSET_MODEL_NAME']
WORKSPACE_ID = os.environ['WORKSPACE_ID']
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def get_asset_model_id():
    # to avoid needing to hardcode asset model id, we can retrieve it from the model name
    asset_model_id = ""
    response = sw_client.list_asset_models(
        maxResults=200
        )
    
    for each_asset_model in response['assetModelSummaries']:
        if each_asset_model['name'] == ASSET_MODEL_NAME:
            asset_model_id = each_asset_model['id']
            return asset_model_id
        
    # if we get here, we didn't find the asset model
    logging.debug("Asset model not found")    
    return False

def get_asset_id(asset_model_id,asset_name_to_check):
    try:
        all_assets = sw_client.list_assets(
            assetModelId=asset_model_id,
            maxResults=200,
            filter='TOP_LEVEL'
            )
        for each_asset in all_assets['assetSummaries']:
            if each_asset['name'] == asset_name_to_check:
                logging.info("Existing asset found")
                return each_asset['id']
        logging.debug("No existing asset found")
        return False
    except:
        logging.debug("Problem retrieving existing assets")
        return False
    
def delete_sitewise_asset(asset_id):
    try:
        response = sw_client.delete_asset(
            assetId=asset_id,
            )
        logging.debug("Asset deleted")
        return True
    except:
        logging.error("Problem deleting asset")
        return False

def delete_twinmaker_dynamic_entity(entity_id):
    try:
        response = tm_client.delete_entity(
            workspaceId=WORKSPACE_ID,
            entityId=entity_id,
            )
        logging.debug("Asset deleted")
        return True
    except:
        logging.error("Problem deleting twinmaker dynamic asset")
        return False
    
def delete_twinmaker_tag(t_entity_id):
    try:
        response = tm_client.delete_entity(
            workspaceId=WORKSPACE_ID,
            entityId=t_entity_id,
            )
        logging.debug("Tag deleted")
        return True
    except:
        logging.error("Problem deleting twinmaker tag")
        return False

def lambda_handler(event, context):
    if 'pallet' in event['body']:
        asset_name = event['body']['pallet']
        entity_id = event['body']['dynamic_entity_id']
        tag_entity_id = event['body']['tag_entity_id']
        asset_model_id = get_asset_model_id()
        try:
            asset_id = get_asset_id(asset_model_id, asset_name)
            if asset_id:
                delete_sitewise_asset(asset_id)
                delete_twinmaker_dynamic_entity(entity_id)
                delete_twinmaker_tag(tag_entity_id)
        except:
            logging.error("Problem retrieving asset id")
            return {
                'statusCode': 400,
                'body': "Problem retrieving asset id"
            }
    else:
        logging.error("No pallet name")
        return {
            'statusCode': 400,
            'body': "No pallet name provided"
        }

    return {
        'statusCode': 200,
        'body': "ok"
    }