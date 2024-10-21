import os
import json
import boto3
import logging
    
iot_twinmaker = boto3.client('iottwinmaker')
WORKSPACE_ID = os.environ['WORKSPACE_ID']
s3 = boto3.resource('s3')

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def get_model_file_s3():
    logging.info("Getting workspace bucket")
    response = iot_twinmaker.get_workspace(
        workspaceId = WORKSPACE_ID
        )
    bucket_arn = response['s3Location']
    bucket_name = bucket_arn.split(':')[-1]
    return "s3://"+bucket_name+"/full-pallet.glb"

def lambda_handler(event, context):
    logging.debug(event)
    try:
        source_entity_id = event['body']['source_entity_id']
        source_entity_name = event['body']['pallet']
        dynamic_entity_name = source_entity_name+"_dynamic"
        parent_scene_entity_id = event['body']['scene_parent']
        glb_model_file = get_model_file_s3()
        
        output = event['body']
        
        response = iot_twinmaker.create_entity(
            workspaceId=WORKSPACE_ID,
            entityName=dynamic_entity_name,
            components={
                "ModelRef": {
                    "componentTypeId": "com.amazon.iottwinmaker.3d.component.modelref",
                    "properties": {
                        "castShadow": {
                            "definition": {
                                "dataType": {
                                    "type": "BOOLEAN"
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": False,
                                "isExternalId": False,
                                "isStoredExternally": False
                            }
                        },
                        "colorBinding": {
                            "definition": {
                                "dataType": {
                                    "type": "MAP",
                                    "nestedType": {
                                        "type": "STRING"
                                    }
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": False,
                                "isExternalId": False,
                                "isStoredExternally": False
                            }
                        },
                        "localScale": {
                            "definition": {
                                "dataType": {
                                    "type": "LIST",
                                    "nestedType": {
                                        "type": "DOUBLE"
                                    }
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": False,
                                "isExternalId": False,
                                "isStoredExternally": False
                            }
                        },
                        "modelType": {
                            "definition": {
                                "dataType": {
                                    "type": "STRING",
                                    "allowedValues": [
                                        {
                                            "stringValue": "GLB"
                                        },
                                        {
                                            "stringValue": "GLTF"
                                        },
                                        {
                                            "stringValue": "Tiles3D"
                                        },
                                        {
                                            "stringValue": "Environment"
                                        }
                                    ]
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": True,
                                "isExternalId": False,
                                "isStoredExternally": False
                            },
                            "value": {
                                "stringValue": "GLB"
                            }
                        },
                        "opacityBinding": {
                            "definition": {
                                "dataType": {
                                    "type": "MAP",
                                    "nestedType": {
                                        "type": "STRING"
                                    }
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": False,
                                "isExternalId": False,
                                "isStoredExternally": False
                            }
                        },
                        "properties": {
                            "definition": {
                                "dataType": {
                                    "type": "MAP",
                                    "nestedType": {
                                        "type": "STRING"
                                    }
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": False,
                                "isExternalId": False,
                                "isStoredExternally": False
                            }
                        },
                        "receiveShadow": {
                            "definition": {
                                "dataType": {
                                    "type": "BOOLEAN"
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": False,
                                "isExternalId": False,
                                "isStoredExternally": False
                            }
                        },
                        "unitOfMeasure": {
                            "definition": {
                                "dataType": {
                                    "type": "STRING",
                                    "allowedValues": [
                                        {
                                            "stringValue": "millimeters"
                                        },
                                        {
                                            "stringValue": "centimeters"
                                        },
                                        {
                                            "stringValue": "decimeters"
                                        },
                                        {
                                            "stringValue": "meters"
                                        },
                                        {
                                            "stringValue": "kilometers"
                                        },
                                        {
                                            "stringValue": "inches"
                                        },
                                        {
                                            "stringValue": "feet"
                                        },
                                        {
                                            "stringValue": "yards"
                                        },
                                        {
                                            "stringValue": "miles"
                                        }
                                    ]
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": False,
                                "isExternalId": False,
                                "isStoredExternally": False
                            }
                        },
                        "uri": {
                            "definition": {
                                "dataType": {
                                    "type": "STRING"
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": True,
                                "isExternalId": False,
                                "isStoredExternally": False
                            },
                            "value": {
                                "stringValue": glb_model_file
                            }
                        }
                    }
                },
                "Node": {
                    "componentTypeId": "com.amazon.iottwinmaker.3d.node",
                    "properties": {
                        "components": {
                            "definition": {
                                "dataType": {
                                    "type": "LIST",
                                    "nestedType": {
                                        "type": "RELATIONSHIP"
                                    }
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": False,
                                "isExternalId": False,
                                "isStoredExternally": False
                            }
                        },
                        "inLayerOf": {
                            "definition": {
                                "dataType": {
                                    "type": "RELATIONSHIP"
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": False,
                                "isExternalId": False,
                                "isStoredExternally": False
                            }
                        },
                        "isVisualOf": {
                            "definition": {
                                "dataType": {
                                    "type": "RELATIONSHIP"
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": False,
                                "isExternalId": False,
                                "isStoredExternally": False
                            },
                            "value": {
                                "relationshipValue": {
                                    "targetEntityId": source_entity_id
                                }
                            }
                        },
                        "name": {
                            "definition": {
                                "dataType": {
                                    "type": "STRING"
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": True,
                                "isExternalId": False,
                                "isStoredExternally": False
                            },
                            "value": {
                                "stringValue": dynamic_entity_name
                            }
                        },
                        "properties": {
                            "definition": {
                                "dataType": {
                                    "type": "MAP",
                                    "nestedType": {
                                        "type": "STRING"
                                    }
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": False,
                                "isExternalId": False,
                                "isStoredExternally": False
                            }
                        },
                        "tranform_reference": {
                            "definition": {
                                "dataType": {
                                    "type": "RELATIONSHIP"
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": False,
                                "isExternalId": False,
                                "isStoredExternally": False
                            }
                        },
                        "transformConstraint_snapToFloor": {
                            "definition": {
                                "dataType": {
                                    "type": "BOOLEAN"
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": False,
                                "isExternalId": False,
                                "isStoredExternally": False
                            }
                        },
                        "transform_position": {
                            "definition": {
                                "dataType": {
                                    "type": "LIST",
                                    "nestedType": {
                                        "type": "DOUBLE"
                                    }
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": False,
                                "isExternalId": False,
                                "isStoredExternally": False
                            },
                            "value": {
                                "listValue": [
                                    {
                                        "doubleValue": 0.0
                                    },
                                    {
                                        "doubleValue": 2.0
                                    },
                                    {
                                        "doubleValue": 0.0
                                    }
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
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": False,
                                "isExternalId": False,
                                "isStoredExternally": False
                            },
                            "value": {
                                "listValue": [
                                    {
                                        "doubleValue": 0.0
                                    },
                                    {
                                        "doubleValue": 0.0
                                    },
                                    {
                                        "doubleValue": 0.0
                                    }
                                ]
                            }
                        },
                        "transform_scale": {
                            "definition": {
                                "dataType": {
                                    "type": "LIST",
                                    "nestedType": {
                                        "type": "DOUBLE"
                                    }
                                },
                                "isTimeSeries": False,
                                "isRequiredInEntity": False,
                                "isExternalId": False,
                                "isStoredExternally": False
                            },
                            "value": {
                                "listValue": [
                                    {
                                        "doubleValue": 1.0
                                    },
                                    {
                                        "doubleValue": 1.0
                                    },
                                    {
                                        "doubleValue": 1.0
                                    }
                                ]
                            }
                        }
                    }
                }
            },
            parentEntityId = parent_scene_entity_id
        )
        
        output['dynamic_entity_id'] = response['entityId']
        return {
            'statusCode': 200,
            'body': output
        }
    except Exception as e:
        logging.error(e)
        return {
            'statusCode': 500,
            'body': "Failed to create dynamic entity"
        }