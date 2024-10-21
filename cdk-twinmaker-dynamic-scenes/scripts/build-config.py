# Use this script as part of a build pipeline for the PiBot website to capture the details that
# need to be populated into awsconfig.ts, such as Cognito user/id pools
# The script should executed as part of the pre-build in the buildspec.yml (example included in the same folder as this script)

import boto3
import argparse

parser = argparse.ArgumentParser(description="Configure AWS parameters for web application")
parser.add_argument('--region', required=True, default="eu-west-1", help="The AWS region you are using")
parser.add_argument('--username', required=True, help="The username to create for the web application")
parser.add_argument('--password', required=True, help="The password to create for the web application")
parser.add_argument('--email', required=True, help="The email address to create for the web application")
args = parser.parse_args()

upclient = boto3.client('cognito-idp', region_name=args.region)
idclient = boto3.client('cognito-identity', region_name=args.region)
iotclient = boto3.client('iot', region_name=args.region)
aws_config_template = "../../react-web/src/awsconfig-template.js"
aws_config_output = "../../react-web/src/awsconfig.js"

# get cognito details
user_pools = upclient.list_user_pools(
	MaxResults = 50
)

for pool in user_pools['UserPools']:
	if pool['Name'] == 'twinmaker_userpool':
		user_pool_id = pool['Id']

user_pool_clients = upclient.list_user_pool_clients(
	UserPoolId = user_pool_id,
	MaxResults = 50
)

for app in user_pool_clients['UserPoolClients']:
	if app['UserPoolId'] == user_pool_id:
		app_id = app['ClientId']
print("app_id: ", app_id)

id_pools = idclient.list_identity_pools(
	MaxResults = 50
)

for idp in id_pools['IdentityPools']:
	if idp['IdentityPoolName'].startswith('identitypool_'):
		id_pool_id = idp['IdentityPoolId']
print("id_pool_id: ", id_pool_id)

# Get IoT Core endpoint
iot_endpoint = iotclient.describe_endpoint(
	endpointType = 'iot:Data-ATS'
)['endpointAddress']
print("iot_endpoint: ", iot_endpoint)

# Sitewise - get asset model property for dwell_time
sitewise_client = boto3.client('iotsitewise', region_name=args.region)
# get asset model id for model with name PalletAssetModel
asset_models = sitewise_client.list_asset_models(
	maxResults = 100
)

for asset_model in asset_models['assetModelSummaries']:
	if asset_model['name'] == 'PalletAssetModel':
		asset_model_id = asset_model['id']
model_properties = sitewise_client.describe_asset_model(
	assetModelId = asset_model_id
)['assetModelProperties']
for prop in model_properties:
	if prop['name'] == 'dwell_time':
		dwell_property = prop['id']

print("dwell_property: ", dwell_property)

# Twinmaker - get palletassetmodel component type id
tm_client = boto3.client('iottwinmaker', region_name=args.region)
workspace_id="PalletMonitoring"

model_types = tm_client.list_component_types(
    workspaceId=workspace_id,
	maxResults=50
)

for comp_type in model_types['componentTypeSummaries']:
	if 'componentTypeName' in comp_type and comp_type['componentTypeName'] == 'PalletAssetModel':
		component_type_id = comp_type['componentTypeId']
print("component_type_id: ", component_type_id)

# Now update awsconfig.ts with correct values
placeholders = ['aws-region','user_pool','id_pool','client_id','iot_endpoint','dwell_property','pallet_component_id']
final_vals = (args.region,user_pool_id,id_pool_id,app_id,iot_endpoint,dwell_property,component_type_id)

with open(aws_config_template,'r', encoding='utf-8') as input:
	config_data = input.read()

for placeholder,final in zip(placeholders,final_vals):
	config_data = config_data.replace(placeholder,final)

with open(aws_config_output, 'w', encoding='utf-8') as output:
	output.write(config_data)

# Create user in userpool for web logon
print("Creating user in Cognito user pool")

upclient.admin_create_user(
	UserPoolId=user_pool_id,
	Username=args.username,
	UserAttributes=[
		{
			'Name': 'email',
			'Value': args.email
		},
		{
			'Name': 'email_verified',
			'Value': 'true'
		}
	],
	MessageAction='SUPPRESS'
)
upclient.admin_set_user_password(
	UserPoolId=user_pool_id,
	Username=args.username,
	Password=args.password,
	Permanent=True
)