import boto3
import json
import time
import logging
import os

client = boto3.client('iotsitewise')
propertyExtIds = ['extid_pallet_barcode','extid_pallet_dwell','extid_goods_type','extid_pallet_weight']
ASSET_MODEL_NAME = os.environ['ASSET_MODEL_NAME']

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    
def get_asset_model_id():
    # to avoid needing to hardcode asset model id, we can retrieve it from the model name
    asset_model_id = ""
    response = client.list_asset_models(
        maxResults=200
        )
    
    for each_asset_model in response['assetModelSummaries']:
        if each_asset_model['name'] == ASSET_MODEL_NAME:
            asset_model_id = each_asset_model['id']
    
    return asset_model_id

def assetExists(asset_model_id,asset_name_to_check):
    try:
        all_assets = client.list_assets(
            assetModelId=asset_model_id,
            maxResults=200,
            filter='TOP_LEVEL'
            )
        for each_asset in all_assets['assetSummaries']:
            if each_asset['name'] == asset_name_to_check:
                logging.info("Existing asset found")
                return True
        logging.info("No existing asset found")
        return False
    except:
        logging.debug("Problem retrieving existing assets")
        return False

def lambda_handler(event, context):
    if event['pallet']:
        asset_name = event['pallet']
        asset_model_id = get_asset_model_id()
        propertyAliases = [asset_name+'/barcode',asset_name+'/dwell_time',asset_name+'/goods_type',asset_name+'/weight']
        logging.debug("Pallet Name: "+asset_name)
        new_asset = "no"

        if not assetExists(asset_model_id,asset_name):
            new_asset = "yes"
            response = client.create_asset(
                assetName = asset_name,
                assetModelId = asset_model_id
                )
            
            # now need to wait for asset to become active (which may take a few seconds)
            active = False
            while not active:
                logging.debug("Checking if new asset is active")
                asset_creating = client.describe_asset(
                    assetId=response['assetId']
                    )
                if asset_creating['assetStatus']['state'] == 'ACTIVE':
                    active = True
                time.sleep(1)
            
            # Associate properties to disassociated datastreams
            for propExtId in propertyExtIds:
                # associate property to data streams that will have been created as disassociated
                # by the original MQTT message
                prop_update = client.associate_time_series_to_asset_property(
                    alias=propertyAliases[propertyExtIds.index(propExtId)],
                    assetId=response['assetId'],
                    propertyId='externalId:'+propExtId
                    )
            
                # Update properties to enable once asset is in active state
                property = client.update_asset_property(
                    propertyId='externalId:'+propExtId,
                    assetId=response['assetId'],
                    propertyAlias=propertyAliases[propertyExtIds.index(propExtId)],
                    propertyNotificationState='ENABLED'
                    )

        #out_msg = { "pallet": asset_name, "new_asset": new_asset, "full_event": event }
        output = event
        output['new_asset'] = new_asset
        output['asset_model_id'] = asset_model_id
        
        return {
            'statusCode': 200,
            'body': output
        }
    else:
        return {
            'statusCode': 400,
            'body': 'pallet not found in event'
        }