import os
import json
import boto3
import logging
    
iot_twinmaker = boto3.client('iottwinmaker')
WORKSPACE_ID = os.environ['WORKSPACE_ID']
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def getDynamicEntityId(name,all_entities):
    # get the TwinMaker entity ID from the name - assumes same as main entity by with a suffix starting with "_"
    dyn_entity = "not_found"
    for entity in all_entities['entitySummaries']:
        if entity['entityName'].startswith(name+"_"):
            #print(entity['entityId'])
            dyn_entity = entity['entityId']
            break
    return dyn_entity
    
def checkAssociated(dyn_entity_id,source_entity_id):
    # check 'isVisualOf' attribute to confirm correct dynamic entity will be updated
    entity_detail = iot_twinmaker.get_entity(
        workspaceId=WORKSPACE_ID,
        entityId=dyn_entity_id
        )
    #print(entity_detail)
    isVisualOfEntity = entity_detail['components']['Node']['properties']['isVisualOf']['value']['relationshipValue']['targetEntityId']
    #print("isVisualOf: "+isVisualOfEntity)
    if isVisualOfEntity == source_entity_id:
        return True
    else:
        return False
        
def checkTag(pallet_name,all_entities):
    # get entityId of associated tag
    tag_entity = "not_found"
    for entity in all_entities['entitySummaries']:
        if entity['entityName'] == "tag_"+pallet_name:
            tag_entity = entity['entityId']
            break
    return tag_entity
    
def lambda_handler(event, context):
    logging.debug(event)
    try:
        all_entities = iot_twinmaker.list_entities(workspaceId=WORKSPACE_ID)
        pallet_name = event['body']['pallet']
        source_entity_id = event['body']['source_entity_id']
        dynamic_entity_id = getDynamicEntityId(pallet_name,all_entities)
        output = event['body']
        
        if not dynamic_entity_id == "not_found":
            if checkAssociated(dynamic_entity_id,source_entity_id):
                output['dynamic_entity_id'] = dynamic_entity_id
                # now get tag
                logging.debug("Found dynamic entity, getting tag entity Id")
                output['tag_entity_id'] = checkTag(pallet_name,all_entities)
                logging.debug(output)
                return {
                    'statusCode': 200,
                    'body': output
                }
            else:
                output['dynamic_entity_id'] = "found_not_linked"
                return {
                    'statusCode': 200,
                    'body': output
                }
        else:
            output['dynamic_entity_id'] = "not_found"
            return {
                'statusCode': 200,
                'body': output
            }     
    except Exception as e:
        logging.error(e)
        return {
            'statusCode': 400,
            'body': 'error'
        }
