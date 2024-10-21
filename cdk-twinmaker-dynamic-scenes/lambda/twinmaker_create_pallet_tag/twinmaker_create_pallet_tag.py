import os
import json
import boto3
import logging
    
iot_twinmaker = boto3.client('iottwinmaker')
iot_sitewise = boto3.client('iotsitewise')
WORKSPACE_ID = os.environ['WORKSPACE_ID']
val_names = ["**Bar%20Code**%20:%20","**Goods%20Type**%20:%20","**Weight(KG)**%20:%20"]

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def get_property_guids(asset_model_id):
    # get the property guids for the barcode, goods and weight properties
    prop_barcode = ""
    prop_goods = ""
    prop_weight = ""
    response = iot_sitewise.describe_asset_model(
        assetModelId=asset_model_id
    )
    props = response['assetModelProperties']
    for prop in props:
        if prop['name'] == 'barcode':
            prop_barcode = prop['id']
        elif prop['name'] == 'goods_type':
            prop_goods = prop['id']
        elif prop['name'] == 'weight':
            prop_weight = prop['id']
    return {"barcode":prop_barcode, "goods_type": prop_goods, "weight": prop_weight}

def get_pallet_details(pallet,property_guids):
    logging.info("Getting pallet details")
    response = iot_sitewise.batch_get_asset_property_value(
        entries=[
            {
                'entryId': "1",
                'assetId': pallet,
                'propertyId': property_guids['barcode']
            },
            {
                'entryId': "2",
                'assetId': pallet,
                'propertyId': property_guids['goods_type']
            },
            {
                'entryId': "3",
                'assetId': pallet,
                'propertyId': property_guids['weight']
            }
        ]
    )
    vals = [d['assetPropertyValue']['value'] for d in response['successEntries']]
    logging.debug(vals)
    return vals

def remove_noise(vals):
    #new_vals = {}
    new_string = ""
    idx = 0
    for item in vals:
        for key in item.keys():
            logging.debug("Value: ",item[key])
            new_string += val_names[idx]+str(item[key])+"%0A"
            idx += 1
    return new_string

def create_tag(tag_name,associated_entity_id,pallet_details):
    logging.info("creating tag for pallet")
    tag_markdown = str(json.dumps(pallet_details))
    
    response = iot_twinmaker.create_entity(
        workspaceId=WORKSPACE_ID,
        entityName=tag_name,
        components={
            "DataOverlay": {
                "componentTypeId": "com.amazon.iottwinmaker.3d.component.dataoverlay",
                "properties": {
                    "dataRows": {
                        "definition": {
                            "dataType": {
                                "type": "LIST",
                                "nestedType": {
                                    "type": "MAP",
                                    "nestedType": {
                                        "type": "STRING"
                                    }
                                }
                            },
                            "isTimeSeries": False,
                            "isRequiredInEntity": True,
                            "isExternalId": False,
                            "isStoredExternally": False
                        },
                        "value": {
                            "listValue": [
                                {
                                    "mapValue": {
                                        "content": {
                                            "stringValue": tag_markdown
                                        },
                                        "rowType": {
                                            "stringValue": "Markdown"
                                        }
                                    }
                                }
                            ]
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
                    "rowBindings": {
                        "definition": {
                            "dataType": {
                                "type": "LIST",
                                "nestedType": {
                                    "type": "MAP",
                                    "nestedType": {
                                        "type": "STRING"
                                    }
                                }
                            },
                            "isTimeSeries": False,
                            "isRequiredInEntity": False,
                            "isExternalId": False,
                            "isStoredExternally": False
                        }
                    },
                    "subType": {
                        "definition": {
                            "dataType": {
                                "type": "STRING",
                                "allowedValues": [
                                    {
                                        "stringValue": "TextAnnotation"
                                    },
                                    {
                                        "stringValue": "OverlayPanel"
                                    }
                                ]
                            },
                            "isTimeSeries": False,
                            "isRequiredInEntity": True,
                            "isExternalId": False,
                            "isStoredExternally": False
                        },
                        "value": {
                            "stringValue": "OverlayPanel"
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
                                "targetEntityId": associated_entity_id
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
                            "stringValue": tag_name
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
                                    "doubleValue": 7.0
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
                                    "doubleValue": 5.0
                                },
                                {
                                    "doubleValue": 5.0
                                },
                                {
                                    "doubleValue": 5.0
                                }
                            ]
                        }
                    }
                }
            },
            "Tag": {
                "componentTypeId": "com.amazon.iottwinmaker.3d.component.tag",
                "properties": {
                    "chosenColor": {
                        "definition": {
                            "dataType": {
                                "type": "STRING"
                            },
                            "isTimeSeries": False,
                            "isRequiredInEntity": False,
                            "isExternalId": False,
                            "isStoredExternally": False
                        }
                    },
                    "customIcon_iconName": {
                        "definition": {
                            "dataType": {
                                "type": "STRING"
                            },
                            "isTimeSeries": False,
                            "isRequiredInEntity": False,
                            "isExternalId": False,
                            "isStoredExternally": False
                        }
                    },
                    "customIcon_prefix": {
                        "definition": {
                            "dataType": {
                                "type": "STRING"
                            },
                            "isTimeSeries": False,
                            "isRequiredInEntity": False,
                            "isExternalId": False,
                            "isStoredExternally": False
                        }
                    },
                    "icon": {
                        "definition": {
                            "dataType": {
                                "type": "STRING"
                            },
                            "isTimeSeries": False,
                            "isRequiredInEntity": False,
                            "isExternalId": False,
                            "isStoredExternally": False
                        },
                        "value": {
                            "stringValue": "Info"
                        }
                    },
                    "navLink_destination": {
                        "definition": {
                            "dataType": {
                                "type": "STRING"
                            },
                            "isTimeSeries": False,
                            "isRequiredInEntity": False,
                            "isExternalId": False,
                            "isStoredExternally": False
                        }
                    },
                    "navLink_params": {
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
                    "offset": {
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
                    "styleBinding": {
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
                    }
                }
            }
        }

    )
    return response

def lambda_handler(event, context):
    logging.debug(event)
    dynamic_entity_id = event['body']['dynamic_entity_id']
    source_entity_id = event['body']['source_entity_id']
    pallet_name = event['body']['pallet']
    asset_model_id = event['body']['asset_model_id']
    output = event['body']

    tag_name = "tag_"+pallet_name
    pallet_property_guids = get_property_guids(asset_model_id)

    tag_data = remove_noise(get_pallet_details(source_entity_id,pallet_property_guids))
    tag = create_tag(tag_name,dynamic_entity_id,tag_data)
    logging.debug(tag)
    output['tag_entity_id'] = tag['entityId']
    logging.debug(output)

    return {
        'statusCode': 200,
        'body': output
    }
