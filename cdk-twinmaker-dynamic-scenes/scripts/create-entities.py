# credit Martin Miller (linkedin.com/in/martinmiller0) for update_json_placeholders function

import json
import boto3
    
iot_twinmaker = boto3.client('iottwinmaker')
workspace_id = "PalletMonitoring"
entities = ['CrossDock-Inbound','CrossDock-Sorting',"CrossDock-Outbound"]
inbound_door_positions = [[2.0,2.0,17],[2.0,2.0,42],[2.0,2.0,67],[2.0,2.0,92],[2.0,2.0,117]]
outbound_door_positions = [[330,2.0,17],[330,2.0,42],[330,2.0,67],[330,2.0,92],[330,2.0,117]]

def get_parent_entity_id(parent):
    print("Getting parent entity ID")
    response = iot_twinmaker.list_entities(
        workspaceId = workspace_id,
        filters = [{ 'parentEntityId' : parent }]
        )
    return response['entitySummaries'][0]['entityId']

def get_workspace_bucket():
    print("Getting workspace bucket")
    response = iot_twinmaker.get_workspace(
        workspaceId = workspace_id
        )
    bucket_arn = response['s3Location']
    bucket_name = bucket_arn.split(':')[-1]
    return bucket_name

def update_json_placeholders(component_json,placeholder,new_val):
    def decode_dict(d):
        if placeholder in d.values():
            for key, value in d.items():
                if value == placeholder:
                    #print(f"Found placeholder {placeholder} at key {key}")
                    d[key] = new_val
        return d
    return json.loads(component_json, object_hook=decode_dict)

def create_entity(entity_name,parent_entity_id,component_json):
    print("Creating entity")
    # create the base scene entities - 3D models of the warehouse
    try:
        response = iot_twinmaker.create_entity(
            workspaceId = workspace_id,
            entityName = entity_name,
            parentEntityId = parent_entity_id,
            components = component_json
            )
    except Exception as e:
        print(e)
        print(f"Error creating entity {entity_name}")
    return

def create_door_entities(parent_entity_id, workspace_bucket):
    door_glb_file = f's3://{workspace_bucket}/dock-door.glb'
    for i, position in enumerate(inbound_door_positions):
        door_entity_name = f"Inbound_Door_{i+1}"
        with open(f'../scene-entities/dock-door.json') as f:
            door_component_json = f.read()
        door_component_json = update_json_placeholders(door_component_json, 'glb_file_location_s3', door_glb_file)
        door_component_json = update_json_placeholders(json.dumps(door_component_json), 'dock-door-name', door_entity_name)
        door_component_json = update_json_placeholders(json.dumps(door_component_json), 'x_pos', position[0])
        door_component_json = update_json_placeholders(json.dumps(door_component_json), 'y_pos', position[1])
        door_component_json = update_json_placeholders(json.dumps(door_component_json), 'z_pos', position[2])
        create_entity(door_entity_name, parent_entity_id, door_component_json)
    for i, position in enumerate(outbound_door_positions):
        door_entity_name = f"Outbound_Door_{i+1}"
        with open(f'../scene-entities/dock-door.json') as f:
            door_component_json = f.read()
        door_component_json = update_json_placeholders(door_component_json, 'glb_file_location_s3', door_glb_file)
        door_component_json = update_json_placeholders(json.dumps(door_component_json), 'dock-door-name', door_entity_name)
        door_component_json = update_json_placeholders(json.dumps(door_component_json), "x_pos", position[0])
        door_component_json = update_json_placeholders(json.dumps(door_component_json), "y_pos", position[1])
        door_component_json = update_json_placeholders(json.dumps(door_component_json), "z_pos", position[2])
        create_entity(door_entity_name, parent_entity_id, door_component_json)

def main():
    try:
        scene_entity = get_parent_entity_id('SCENES_EntityId')
        workspace_bucket = get_workspace_bucket()
        # Create the main scene entities for the inbound, outbound and sorting areas
        for entity in entities:
            print(f"Processing entity {entity}")
            glb_s3_path = f's3://{workspace_bucket}/{entity}.glb'
            print("File path:", glb_s3_path)
            with open(f'../scene-entities/{entity}.json') as f:
                component_json = f.read()
                component_json = update_json_placeholders(component_json,'glb_file_location_s3',glb_s3_path)
            create_entity(entity, scene_entity, component_json)
        # Now add the dock doors for inbound and outbound
        create_door_entities(scene_entity, workspace_bucket)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()