import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as sfn_tasks,
    aws_lambda_event_sources as event_sources,
    aws_lambda as _lambda,
    aws_dynamodb as ddb,
    aws_iam as iam,
    aws_s3 as s3,
    aws_iot as iot,
    aws_s3_deployment as s3_deploy,
    aws_iottwinmaker as twinmaker,
    aws_iotsitewise as sitewise,
    aws_cognito as cognito
)
from constructs import Construct


class CdkTwinmakerDynamicScenesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Variables
        workspace_id = "PalletMonitoring"
        asset_model_name = "PalletAssetModel"


        #######################################################
        # Lambda Functions
        #######################################################

        all_lambda_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "iotsitewise:CreateAsset",
                "iotsitewise:DeleteAsset",
                "iotsitewise:Get*",
                "iotsitewise:Update*",
                "iotsitewise:Describe*",
                "iotsitewise:List*",
                "iotsitewise:Associate*",
                "iotsitewise:BatchPutAssetPropertyValue",
                "iotsitewise:BatchGet*",
                "iottwinmaker:Get*",
                "iottwinmaker:List*",
                "iottwinmaker:CreateEntity",
                "iottwinmaker:UpdateEntity",
                "iottwinmaker:DeleteEntity",
                "iottwinmaker:UpdateScene",
                "iottwinmaker:BatchPutPropertyValues"
            ],
            resources=['*']
        )

        sitewise_create_asset_function = _lambda.Function(
            self,
            "sitewise_create_asset",
            runtime=_lambda.Runtime.PYTHON_3_12,
            environment= {
                "ASSET_MODEL_NAME": asset_model_name
            },
            handler="sitewise_create_asset.lambda_handler",
            code=_lambda.Code.from_asset("lambda/sitewise_create_asset"),
            initial_policy=[all_lambda_policy],
            timeout=cdk.Duration.seconds(60)
        )

        twinmaker_get_parent_entities_function = _lambda.Function(
            self,
            "twinmaker_get_parent_entities",
            runtime=_lambda.Runtime.PYTHON_3_12,
            environment= {
                "WORKSPACE_ID": workspace_id
            },
            handler="get_scene_entities.lambda_handler",
            code=_lambda.Code.from_asset("lambda/twinmaker_get_scene_entities"),
            initial_policy=[all_lambda_policy],
            timeout=cdk.Duration.seconds(10)
        )

        twinmaker_check_source_entity_function = _lambda.Function(
            self,
            "twinmaker_check_source_entity",
            runtime=_lambda.Runtime.PYTHON_3_12,
            environment= {
                "WORKSPACE_ID": workspace_id
            },
            handler="twinmaker_check_source_entity.lambda_handler",
            code=_lambda.Code.from_asset("lambda/twinmaker_check_source_entity"),
            initial_policy=[all_lambda_policy],
            timeout=cdk.Duration.seconds(30)
        )

        twinmaker_check_dynamic_entity_function = _lambda.Function(
            self,
            "twinmaker_check_dynamic_entity",
            runtime=_lambda.Runtime.PYTHON_3_12,
            environment= {
                "WORKSPACE_ID": workspace_id
            },
            handler="twinmaker_check_dynamic_entity.lambda_handler",
            code=_lambda.Code.from_asset("lambda/twinmaker_check_dynamic_entity"),
            initial_policy=[all_lambda_policy],
            timeout=cdk.Duration.seconds(30)
        )

        twinmaker_create_dynamic_entity_function = _lambda.Function(
            self,
            "twinmaker_create_dynamic_entity",
            runtime=_lambda.Runtime.PYTHON_3_12,
            environment= {
                "WORKSPACE_ID": workspace_id
            },
            handler="twinmaker_create_dynamic_entity.lambda_handler",
            code=_lambda.Code.from_asset("lambda/twinmaker_create_dynamic_entity"),
            initial_policy=[all_lambda_policy],
            timeout=cdk.Duration.seconds(60)
        )

        twinmaker_create_pallet_tag_function = _lambda.Function(
            self,
            "twinmaker_create_pallet_tag",
            runtime=_lambda.Runtime.PYTHON_3_12,
            environment= {
                "WORKSPACE_ID": workspace_id
            },
            handler="twinmaker_create_pallet_tag.lambda_handler",
            code=_lambda.Code.from_asset("lambda/twinmaker_create_pallet_tag"),
            initial_policy=[all_lambda_policy],
            timeout=cdk.Duration.seconds(60)
        )

        get_location_coordinates_function = _lambda.Function(
            self,
            "get_location_coordinates",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="get_location_coordinates.lambda_handler",
            code=_lambda.Code.from_asset("lambda/get_location_coordinates"),
            initial_policy=[all_lambda_policy],
            timeout=cdk.Duration.seconds(10)
        )

        twinmaker_update_pallet_location_function = _lambda.Function(
            self,
            "twinmaker_update_pallet_location",
            runtime=_lambda.Runtime.PYTHON_3_12,
            environment= {
                "WORKSPACE_ID": workspace_id
            },
            handler="twinmaker_update_pallet_location.lambda_handler",
            code=_lambda.Code.from_asset("lambda/twinmaker_update_pallet_location"),
            initial_policy=[all_lambda_policy],
            timeout=cdk.Duration.seconds(30)
        )

        twinmaker_sitewise_delete_asset = _lambda.Function(
            self,
            "delete_sitewise_twinmaker_asset",
            runtime=_lambda.Runtime.PYTHON_3_12,
            environment= {
                "WORKSPACE_ID": workspace_id,
                "ASSET_MODEL_NAME": asset_model_name
            },
            handler="delete_sitewise_twinmaker_asset.lambda_handler",
            code=_lambda.Code.from_asset("lambda/delete_sitewise_twinmaker_asset"),
            initial_policy=[all_lambda_policy],
            timeout=cdk.Duration.seconds(30)
        )

        twinmaker_change_door_state_function = _lambda.Function(
            self,
            "twinmaker_change_door_state",
            runtime=_lambda.Runtime.PYTHON_3_12,
            environment= {
                "WORKSPACE_ID": workspace_id
            },
            handler="twinmaker_change_door_state.lambda_handler",
            code=_lambda.Code.from_asset("lambda/twinmaker_change_door_state"),
            initial_policy=[all_lambda_policy],
            timeout=cdk.Duration.seconds(30)
        )

        #######################################################
        # Step Functions
        #######################################################

        # Start State
        start_state = sfn.Pass(self, "Start")

        # Wait for 10 seconds state
        wait_10 = sfn.Wait(self, "Wait 10 Seconds", time=sfn.WaitTime.duration(cdk.Duration.seconds(10)))

        # Lambda States
        create_sitewise_asset = sfn_tasks.LambdaInvoke(
            self, "CreateSitewiseAsset",
            lambda_function=sitewise_create_asset_function,
            output_path="$.Payload"
        )
        get_twinmaker_parent_entities = sfn_tasks.LambdaInvoke(
            self, "GetParentTwinMakerEntities",
            lambda_function=twinmaker_get_parent_entities_function,
            output_path="$.Payload"
        )
        check_source_entity = sfn_tasks.LambdaInvoke(
            self, "CheckSourceEntity",
            lambda_function=twinmaker_check_source_entity_function,
            output_path="$.Payload"
        )
        check_dynamic_entity = sfn_tasks.LambdaInvoke(
            self, "CheckDynamicEntity",
            lambda_function=twinmaker_check_dynamic_entity_function,
            output_path="$.Payload"
        )
        create_dynamic_entity = sfn_tasks.LambdaInvoke(
            self, "CreateDynamicEntity",
            lambda_function=twinmaker_create_dynamic_entity_function,
            output_path="$.Payload"
        )
        create_pallet_tag = sfn_tasks.LambdaInvoke(
            self, "CreatePalletTag",
            lambda_function=twinmaker_create_pallet_tag_function,
            output_path="$.Payload"
        )
        get_location_coordinates = sfn_tasks.LambdaInvoke(
            self, "GetLocationCoordinates",
            lambda_function=get_location_coordinates_function,
            output_path="$.Payload"
        )
        update_pallet_location = sfn_tasks.LambdaInvoke(
            self, "UpdatePalletLocation",
            lambda_function=twinmaker_update_pallet_location_function,
            output_path="$.Payload"
        )
        delete_pallet = sfn_tasks.LambdaInvoke(
            self, "DeletePallet",
            lambda_function=twinmaker_sitewise_delete_asset,
            output_path="$.Payload"
        )

        # End state
        end_state = sfn.Pass(self, "End")

        # Full Step Function Definition
        step_flow = start_state.next(
            create_sitewise_asset.next(
                get_twinmaker_parent_entities.next(
                    check_source_entity.next(
                        sfn.Choice(self, "SourceEntityExists")
                            .when(sfn.Condition.string_equals("$.body.source_entity_status", "not_found"), wait_10
                                .next(check_source_entity))
                            .otherwise(
                                check_dynamic_entity.next(
                                    sfn.Choice(self, "DynamicEntityExists")
                                        .when(sfn.Condition.string_equals("$.body.dynamic_entity_id", "not_found"), create_dynamic_entity
                                            .next(create_pallet_tag
                                                    .next(get_location_coordinates
                                                        .next(update_pallet_location
                                                                .next(end_state)))))
                                        .when(sfn.Condition.string_equals("$.body.status", "loaded"), delete_pallet
                                            .next(end_state))
                                        .otherwise(get_location_coordinates)
                                )
                            )
                        )
                    )
                )
            )

        pallet_orchestration_step_function = sfn.StateMachine(
            self, "pallet_orchestration_step_function",
            definition_body = sfn.DefinitionBody.from_chainable(step_flow)
        )

        #######################################################
        # IoT Core Rules
        #######################################################

        # IAM policy and role to allow the rules to carry out actions for sitewise and step function
        iot_rule_action_policy = iam.PolicyDocument(
            statements=[iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['iotsitewise:BatchPutAssetPropertyValue','states:StartExecution'],
            resources=['*']
            )]
        )

        iot_rule_role_assume_policy = iam.PolicyDocument(
            statements=[iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=['sts:AssumeRole'],
                principals=[iam.ServicePrincipal('iot.amazonaws.com')]
            )]
        )
        iot_rule_role = iam.CfnRole(
            self, "iot_rule_role",
            assume_role_policy_document=iot_rule_role_assume_policy,
            policies=[iam.CfnRole.PolicyProperty(
                policy_name="iot_rule_actions_policy",
                policy_document=iot_rule_action_policy
            )]
        )

        # IoT Core Rule to trigger step function from MQTT topic
        pallet_topic_rule = iot.CfnTopicRule(self, "update_pallet_rule",
            rule_name="pallet_orchestration_rule",
            topic_rule_payload=iot.CfnTopicRule.TopicRulePayloadProperty(
                sql="SELECT * FROM 'pallet_data'",
                actions=[iot.CfnTopicRule.ActionProperty(
                    step_functions=iot.CfnTopicRule.StepFunctionsActionProperty(
                        execution_name_prefix="pallet_orchestration_execution",
                        state_machine_name=pallet_orchestration_step_function.state_machine_name,
                        role_arn=iot_rule_role.attr_arn
                    )
                ),
                iot.CfnTopicRule.ActionProperty(
                    iot_site_wise=iot.CfnTopicRule.IotSiteWiseActionProperty(
                        put_asset_property_value_entries=[iot.CfnTopicRule.PutAssetPropertyValueEntryProperty(
                            property_values=[iot.CfnTopicRule.AssetPropertyValueProperty(
                                timestamp=iot.CfnTopicRule.AssetPropertyTimestampProperty(
                                    time_in_seconds="${floor(timestamp() / 1E3)}"
                                ),
                                value=iot.CfnTopicRule.AssetPropertyVariantProperty(
                                    string_value="${barcode}"
                                )
                            )],
                            property_alias="${pallet}/barcode",
                            entry_id="1"
                        ),
                        iot.CfnTopicRule.PutAssetPropertyValueEntryProperty(
                            property_values=[iot.CfnTopicRule.AssetPropertyValueProperty(
                                timestamp=iot.CfnTopicRule.AssetPropertyTimestampProperty(
                                    time_in_seconds="${floor(timestamp() / 1E3)}"
                                ),
                                value=iot.CfnTopicRule.AssetPropertyVariantProperty(
                                    integer_value="${weight}"
                                )
                            )],
                            property_alias="${pallet}/weight",
                            entry_id="2"
                        ),
                        iot.CfnTopicRule.PutAssetPropertyValueEntryProperty(
                            property_values=[iot.CfnTopicRule.AssetPropertyValueProperty(
                                timestamp=iot.CfnTopicRule.AssetPropertyTimestampProperty(
                                    time_in_seconds="${floor(timestamp() / 1E3)}"
                                ),
                                value=iot.CfnTopicRule.AssetPropertyVariantProperty(
                                    string_value="${goods_type}"
                                )
                            )],
                            property_alias="${pallet}/goods_type",
                            entry_id="3"
                        ),
                        iot.CfnTopicRule.PutAssetPropertyValueEntryProperty(
                            property_values=[iot.CfnTopicRule.AssetPropertyValueProperty(
                                timestamp=iot.CfnTopicRule.AssetPropertyTimestampProperty(
                                    time_in_seconds="${floor(timestamp() / 1E3)}"
                                ),
                                value=iot.CfnTopicRule.AssetPropertyVariantProperty(
                                    integer_value="${dwell_time}"
                                )
                            )],
                            property_alias="${pallet}/dwell_time",
                            entry_id="4"
                        )],
                        role_arn=iot_rule_role.attr_arn
                    )
                )]
            )
        )
        
        # IoT Rule to allow updating of door state (open/closed)
        # need to check if update required to set Lambda version to $LATEST as part of the action
        door_topic_rule = iot.CfnTopicRule(self, "change_door_state_rule",
            rule_name="door_state_rule",
            topic_rule_payload=iot.CfnTopicRule.TopicRulePayloadProperty(
                sql="SELECT * FROM 'door_state'",
                actions=[iot.CfnTopicRule.ActionProperty(
                    lambda_=iot.CfnTopicRule.LambdaActionProperty(
                        function_arn=twinmaker_change_door_state_function.function_arn
                    )
                )]
            )
        )

        #######################################################
        # SiteWise
        #######################################################

        # Create SiteWise asset model for pallet
        pallet_asset_model = sitewise.CfnAssetModel(self, "pallet_asset_model",
            asset_model_name="PalletAssetModel",
            asset_model_description="Pallet Asset Model",
            asset_model_properties=[
                sitewise.CfnAssetModel.AssetModelPropertyProperty(
                    name="id",
                    data_type="STRING",
                    external_id="extid_pallet_id",
                    type=sitewise.CfnAssetModel.PropertyTypeProperty(
                        type_name="Attribute",
                        attribute=sitewise.CfnAssetModel.AttributeProperty(
                            default_value="none"
                        )
                    )
                ),
                sitewise.CfnAssetModel.AssetModelPropertyProperty(
                    name="barcode",
                    data_type="STRING",
                    external_id="extid_pallet_barcode",
                    type=sitewise.CfnAssetModel.PropertyTypeProperty(
                        type_name="Measurement" 
                    )
                ),
                sitewise.CfnAssetModel.AssetModelPropertyProperty(
                    name="dwell_time",
                    data_type="INTEGER",
                    external_id="extid_pallet_dwell",
                    unit="SECONDS",
                    type=sitewise.CfnAssetModel.PropertyTypeProperty(
                        type_name="Measurement" 
                    )
                ),
                sitewise.CfnAssetModel.AssetModelPropertyProperty(
                    name="location",
                    data_type="STRING",
                    external_id="extid_pallet_location",
                    type=sitewise.CfnAssetModel.PropertyTypeProperty(
                        type_name="Measurement" 
                    )
                ),
                sitewise.CfnAssetModel.AssetModelPropertyProperty(
                    name="goods_type",
                    data_type="STRING",
                    external_id="extid_goods_type",
                    type=sitewise.CfnAssetModel.PropertyTypeProperty(
                        type_name="Measurement" 
                    )
                ),
                sitewise.CfnAssetModel.AssetModelPropertyProperty(
                    name="weight",
                    data_type="INTEGER",
                    external_id="extid_pallet_weight",
                    unit="KG",
                    type=sitewise.CfnAssetModel.PropertyTypeProperty(
                        type_name="Measurement" 
                    )
                ),
            ]
        )

        #######################################################
        # TwinMaker
        #######################################################

        # Create S3 bucket for TwinMaker workspace
        s3_bucket = s3.Bucket(self, "twinmaker_workspace_bucket")

        s3_deployment = s3_deploy.BucketDeployment(
            self, "DeploySceneFiles",
            destination_bucket=s3_bucket,
            sources=[s3_deploy.Source.asset("./scene")],
            destination_key_prefix="/"
        )

        # Add CORS policy to S3 bucket
        s3_bucket.add_cors_rule(
            allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.POST, s3.HttpMethods.PUT, s3.HttpMethods.HEAD],
            allowed_origins=["*"],
            allowed_headers=["*"],
            max_age=3000
        )

        # Create Twinmaker Dashboard IAM role
        twinmaker_assume_role_policy_doc = iam.PolicyDocument(
            statements=[iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=['sts:AssumeRole'],
                principals=[iam.ServicePrincipal('iottwinmaker.amazonaws.com')]
            )]
        )

        twinmaker_s3_access_policy = iam.PolicyDocument(
            statements=[iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['s3:Get*','s3:List*','s3:Put*','s3:Delete*'],
            resources=[s3_bucket.bucket_arn,s3_bucket.bucket_arn+"/*"]
            )]
        )

        twinmaker_role = iam.CfnRole(
            self, "twinmaker_role",
            assume_role_policy_document=twinmaker_assume_role_policy_doc,
            policies=[iam.CfnRole.PolicyProperty(
                policy_name="twinmaker_s3_access_policy",
                policy_document=twinmaker_s3_access_policy
            )]
        )

        # Twinmaker IAM role for asset sync from SiteWise
        asset_sync_policy = iam.PolicyDocument(
            statements=[iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['iotsitewise:*','iottwinmaker:*'],
            resources=['*']
            )]
        )
        
        sitewise_asset_sync_role = iam.CfnRole(
            self, "sitewise_asset_sync_role",
            assume_role_policy_document=twinmaker_assume_role_policy_doc,
            policies=[iam.CfnRole.PolicyProperty(
                policy_name="sitewise_asset_sync_policy",
                policy_document=asset_sync_policy
            )]
        )

        # Create TwinMaker workspace
        workspace = twinmaker.CfnWorkspace(self, "PalletMonitoring",
            workspace_id="PalletMonitoring",
            description="Workspace for pallet monitoring",
            role=twinmaker_role.attr_arn,
            s3_location=s3_bucket.bucket_arn
        )

        sitewise_sync = twinmaker.CfnSyncJob(self, "sitewise_sync",
            workspace_id=workspace.workspace_id,
            sync_role=sitewise_asset_sync_role.attr_arn,
            sync_source="SITEWISE"
        )
        sitewise_sync.add_dependency(workspace)
        sitewise_sync.add_dependency(sitewise_asset_sync_role)

        # Create TwinMaker scene
        pallet_scene = twinmaker.CfnScene(self, "pallet_scene",
            scene_id="PalletScene",
            workspace_id=workspace.workspace_id,
            content_location="s3://"+s3_bucket.bucket_domain_name+"/pallet_scene.json",
            description="Scene for pallet monitoring"
        )
        pallet_scene.add_dependency(workspace)
        pallet_scene.add_dependency(sitewise_sync)

        #######################################################
        # Cognito
        #######################################################
        
        # Cognito identity pool and userpool
        user_pool = cognito.UserPool(self, "user_pool",
            user_pool_name="twinmaker_userpool",
            self_sign_up_enabled=False,
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            sign_in_aliases=cognito.SignInAliases(
                email=True,
                username=True,
                phone=False
            ),
            standard_attributes=cognito.StandardAttributes(email=cognito.StandardAttribute(required=True, mutable=True))
        )

        user_pool_client = user_pool.add_client("user_pool_client",
            generate_secret=False,
            auth_flows=cognito.AuthFlow(user_password=True),
            supported_identity_providers=[cognito.UserPoolClientIdentityProvider.COGNITO]
        )

        identity_pool = cognito.CfnIdentityPool(self, "identity_pool",
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                client_id=user_pool_client.user_pool_client_id,
                provider_name=user_pool.user_pool_provider_name
            )]
        )

        # Authenticated and un-authenticated roles, userpool, ID pool, userpool client
        cognito_assume_role_policy_statement = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['sts:AssumeRoleWithWebIdentity']
        )
        cognito_assume_role_policy_statement.add_federated_principal('cognito-identity.amazonaws.com',
            conditions={'StringEquals': {'cognito-identity.amazonaws.com:aud': identity_pool.ref },
                        'ForAnyValue:StringLike': {'cognito-identity.amazonaws.com:amr': 'authenticated'}})

        cognito_assume_role_policy_doc = iam.PolicyDocument(
            statements=[cognito_assume_role_policy_statement]
        )

        cognito_auth_policy = iam.PolicyDocument(
            statements=[iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['mobileanalytics:PutEvents',
                     'cognito-sync:*',
                     'cognito-identity:*',
                     'iottwinmaker:Get*',
                     'iottwinmaker:List*',
                     'iottwinmaker:Describe*',
                     'iottwinmaker:Execute*',
                     's3:Get*',
                     's3:List*'
                     ],
            resources=['*']
            )]
        )

        cognito_unauth_policy = iam.PolicyDocument(
            statements=[iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['mobileanalytics:PutEvents','cognito-sync:*','cognito-identity:GetCredentialsForIdentity'],
            resources=['*']
            )]
        )

        cognito_auth_role = iam.CfnRole(self, "cognito_auth_role",
            assume_role_policy_document=cognito_assume_role_policy_doc,
            policies=[iam.CfnRole.PolicyProperty(
                policy_name="cog_auth_policy",
                policy_document=cognito_auth_policy
            )]
        )

        cognito_unauth_role = iam.CfnRole(self, "cognito_unauth_role",
            assume_role_policy_document=cognito_assume_role_policy_doc,
            policies=[iam.CfnRole.PolicyProperty(
                policy_name="cog_unauth_policy",
                policy_document=cognito_unauth_policy
            )]
        )

        # Attach IAM roles to Cognito ID Pool
        idpool_role_attachment = cognito.CfnIdentityPoolRoleAttachment(self, "idpool_role_attachment",
            identity_pool_id=identity_pool.ref,
            roles={
                "authenticated": cognito_auth_role.attr_arn,
                "unauthenticated": cognito_unauth_role.attr_arn
            }
        )
        idpool_role_attachment.add_dependency(cognito_auth_role)