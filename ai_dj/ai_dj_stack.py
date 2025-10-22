import os

from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_apigatewayv2 as apigw,
    aws_apigatewayv2_integrations as integrations,
    aws_iam as iam,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    Duration,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct


class AiDjStack(Stack):
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        spotify_client_id: str,
        spotify_client_secret: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ========================================
        # DynamoDB Table
        # ========================================
        users_table = dynamodb.Table(
            self,
            "AI-DJ-Users",
            table_name="AI-DJ-Users",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # For development - change in production
            point_in_time_recovery=True,
        )

        # ========================================
        # Lambda Layer for Dependencies
        # ========================================
        dependencies_layer = _lambda.LayerVersion(
            self,
            "DependenciesLayer",
            code=_lambda.Code.from_asset("lambda_layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            description="Dependencies for AI DJ Lambda (requests, boto3)",
        )

        # ========================================
        # Lambda Functions
        # ========================================
        
        # Main playlist handler (original)
        lambda_function = _lambda.Function(
            self,
            "AI-DJ-Handler",
            function_name="AI-DJ-Handler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.lambda_handler",
            code=_lambda.Code.from_asset("lambda_src"),
            layers=[dependencies_layer],
            timeout=Duration.seconds(60),
            memory_size=512,
            environment={
                "SPOTIFY_CLIENT_ID": spotify_client_id,
                "SPOTIFY_CLIENT_SECRET": spotify_client_secret,
                "DYNAMODB_TABLE_NAME": users_table.table_name,
                "BEDROCK_MODEL_ID": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            },
        )
        
        # AgentCore handler for conversational playlist creation
        agent_lambda = _lambda.Function(
            self,
            "AI-DJ-Agent-Handler",
            function_name="AI-DJ-Agent-Handler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="agent_handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_src"),
            layers=[dependencies_layer],
            timeout=Duration.seconds(29),  # Just under API Gateway 30s limit
            memory_size=1536,  # More memory = faster execution (1.5x CPU)
            environment={
                "SPOTIFY_CLIENT_ID": spotify_client_id,
                "SPOTIFY_CLIENT_SECRET": spotify_client_secret,
                "DYNAMODB_TABLE_NAME": users_table.table_name,
                "BEDROCK_MODEL_ID": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            },
        )
        
        # Image/Video handler with Nova Act
        image_lambda = _lambda.Function(
            self,
            "AI-DJ-Image-Handler",
            function_name="AI-DJ-Image-Handler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="image_handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_src"),
            layers=[dependencies_layer],
            timeout=Duration.seconds(90),
            memory_size=1024,
            environment={
                "SPOTIFY_CLIENT_ID": spotify_client_id,
                "SPOTIFY_CLIENT_SECRET": spotify_client_secret,
                "DYNAMODB_TABLE_NAME": users_table.table_name,
                "BEDROCK_MODEL_ID": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
                "NOVA_MODEL_ID": "us.amazon.nova-lite-v1:0",
            },
        )
        
        # Knowledge handler with Amazon Q
        knowledge_lambda = _lambda.Function(
            self,
            "AI-DJ-Knowledge-Handler",
            function_name="AI-DJ-Knowledge-Handler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="knowledge_handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_src"),
            layers=[dependencies_layer],
            timeout=Duration.seconds(60),
            memory_size=512,
            environment={
                "BEDROCK_MODEL_ID": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            },
        )

        # Lambda 5: Access Request Handler
        access_request_lambda = _lambda.Function(
            self,
            "AI-DJ-Access-Request-Handler",
            function_name="AI-DJ-Access-Request-Handler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="access_request_handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_src"),
            layers=[dependencies_layer],
            timeout=Duration.seconds(10),
            memory_size=256,
            environment={
                "DYNAMODB_TABLE_NAME": users_table.table_name,
            },
        )
        
        admin_username = os.environ.get("ADMIN_USERNAME")
        admin_password = os.environ.get("ADMIN_PASSWORD")

        if not admin_username or not admin_password:
            raise ValueError("ADMIN_USERNAME and ADMIN_PASSWORD environment variables must be set before deploying.")

        # Lambda 6: Admin Handler (list access requests)
        admin_lambda = _lambda.Function(
            self,
            "AI-DJ-Admin-Handler",
            function_name="AI-DJ-Admin-Handler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="admin_handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_src"),
            layers=[dependencies_layer],
            timeout=Duration.seconds(10),
            memory_size=256,
            environment={
                "DYNAMODB_TABLE_NAME": users_table.table_name,
                "ADMIN_USERNAME": admin_username,
                "ADMIN_PASSWORD": admin_password,
            },
        )
        
        # Lambda 7: Admin Approve Handler
        admin_approve_lambda = _lambda.Function(
            self,
            "AI-DJ-Admin-Approve-Handler",
            function_name="AI-DJ-Admin-Approve-Handler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="admin_approve_handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_src"),
            layers=[dependencies_layer],
            timeout=Duration.seconds(10),
            memory_size=256,
            environment={
                "DYNAMODB_TABLE_NAME": users_table.table_name,
                "ADMIN_USERNAME": admin_username,
                "ADMIN_PASSWORD": admin_password,
            },
        )
        
        # Lambda 8: Check Authorization Handler
        check_auth_lambda = _lambda.Function(
            self,
            "AI-DJ-Check-Auth-Handler",
            function_name="AI-DJ-Check-Auth-Handler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="check_authorization_handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_src"),
            layers=[dependencies_layer],
            timeout=Duration.seconds(10),
            memory_size=256,
            environment={
                "DYNAMODB_TABLE_NAME": users_table.table_name,
            },
        )

        # Lambda 9: Manual Email Handler
        manual_email_lambda = _lambda.Function(
            self,
            "AI-DJ-Manual-Email-Handler",
            function_name="AI-DJ-Manual-Email-Handler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="manual_email_handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_src"),
            layers=[dependencies_layer],
            timeout=Duration.seconds(10),
            memory_size=256,
            environment={
                "DYNAMODB_TABLE_NAME": users_table.table_name,
            },
        )

        # ========================================
        # IAM Permissions
        # ========================================
        
        # Permissions for DynamoDB (all lambdas)
        for lambda_fn in [lambda_function, agent_lambda, image_lambda, knowledge_lambda, access_request_lambda, admin_lambda, admin_approve_lambda, check_auth_lambda, manual_email_lambda]:
            users_table.grant_read_write_data(lambda_fn)

        # Permissions for Amazon Bedrock (all lambdas)
        bedrock_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock-agent-runtime:InvokeAgent",
            ],
            resources=[
                # Foundation models (serverless) - all regions
                "arn:aws:bedrock:*::foundation-model/*",
                # Inference profiles - all regions
                f"arn:aws:bedrock:*:{self.account}:inference-profile/*",
                # Agents
                f"arn:aws:bedrock:*:{self.account}:agent/*",
                f"arn:aws:bedrock:*:{self.account}:agent-alias/*/*",
            ],
        )
        
        marketplace_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["aws-marketplace:ViewSubscriptions"],
            resources=["*"],
        )
        
        for lambda_fn in [lambda_function, agent_lambda, image_lambda, knowledge_lambda]:
            lambda_fn.add_to_role_policy(bedrock_policy)
            lambda_fn.add_to_role_policy(marketplace_policy)
        
        # Additional permissions for Amazon Q (knowledge lambda)
        knowledge_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "qbusiness:Chat",
                    "qbusiness:ChatSync",
                ],
                resources=[f"arn:aws:qbusiness:*:{self.account}:application/*"],
            )
        )

        # ========================================
        # API Gateway HTTP API
        # ========================================
        http_api = apigw.HttpApi(
            self,
            "AI-DJ-API",
            api_name="AI-DJ-API",
            description="API Gateway for AI DJ Playlist Generator",
            cors_preflight=apigw.CorsPreflightOptions(
                allow_origins=["*"],
                allow_methods=[
                    apigw.CorsHttpMethod.GET,
                    apigw.CorsHttpMethod.POST,
                    apigw.CorsHttpMethod.OPTIONS
                ],
                allow_headers=[
                    "Content-Type",
                    "Authorization",
                    "x-admin-user",
                    "x-admin-pass"
                ],
            ),
        )

        # Lambda Integrations
        lambda_integration = integrations.HttpLambdaIntegration(
            "LambdaIntegration",
            lambda_function,
        )
        
        agent_integration = integrations.HttpLambdaIntegration(
            "AgentIntegration",
            agent_lambda,
        )
        
        image_integration = integrations.HttpLambdaIntegration(
            "ImageIntegration",
            image_lambda,
        )
        
        knowledge_integration = integrations.HttpLambdaIntegration(
            "KnowledgeIntegration",
            knowledge_lambda,
        )

        # API Routes
        # POST /playlist - Original one-shot playlist creation
        http_api.add_routes(
            path="/playlist",
            methods=[apigw.HttpMethod.POST],
            integration=lambda_integration,
        )
        
        # POST /agent/chat - Conversational playlist creation (AgentCore)
        http_api.add_routes(
            path="/agent/chat",
            methods=[apigw.HttpMethod.POST],
            integration=agent_integration,
        )
        
        # POST /playlist-from-image - Image/video-based playlist (Nova Act)
        http_api.add_routes(
            path="/playlist-from-image",
            methods=[apigw.HttpMethod.POST],
            integration=image_integration,
        )
        
        # POST /music-knowledge - Music knowledge queries (Amazon Q)
        http_api.add_routes(
            path="/music-knowledge",
            methods=[apigw.HttpMethod.POST],
            integration=knowledge_integration,
        )
        
        # POST /access-request - Access request submissions
        access_request_integration = integrations.HttpLambdaIntegration(
            "AccessRequestIntegration",
            access_request_lambda,
        )
        
        http_api.add_routes(
            path="/access-request",
            methods=[apigw.HttpMethod.POST, apigw.HttpMethod.OPTIONS],
            integration=access_request_integration,
        )
        
        # GET /admin/requests - Admin: list all access requests
        admin_integration = integrations.HttpLambdaIntegration(
            "AdminIntegration",
            admin_lambda,
        )
        
        http_api.add_routes(
            path="/admin/requests",
            methods=[apigw.HttpMethod.GET, apigw.HttpMethod.OPTIONS],
            integration=admin_integration,
        )
        
        # POST /admin/approve - Admin: approve/reject user
        admin_approve_integration = integrations.HttpLambdaIntegration(
            "AdminApproveIntegration",
            admin_approve_lambda,
        )
        
        http_api.add_routes(
            path="/admin/approve",
            methods=[apigw.HttpMethod.POST, apigw.HttpMethod.OPTIONS],
            integration=admin_approve_integration,
        )
        
        # POST /check-authorization - Check if user is authorized
        check_auth_integration = integrations.HttpLambdaIntegration(
            "CheckAuthIntegration",
            check_auth_lambda,
        )
        
        http_api.add_routes(
            path="/check-authorization",
            methods=[apigw.HttpMethod.POST, apigw.HttpMethod.OPTIONS],
            integration=check_auth_integration,
        )

        # POST /manual-email - Manual email submissions when Spotify profile is blocked
        manual_email_integration = integrations.HttpLambdaIntegration(
            "ManualEmailIntegration",
            manual_email_lambda,
        )

        http_api.add_routes(
            path="/manual-email",
            methods=[apigw.HttpMethod.POST, apigw.HttpMethod.OPTIONS],
            integration=manual_email_integration,
        )

        # ========================================
        # Outputs
        # ========================================
        CfnOutput(
            self,
            "ApiEndpoint",
            value=http_api.url or "N/A",
            description="API Gateway endpoint URL",
            export_name="AI-DJ-API-Endpoint",
        )

        CfnOutput(
            self,
            "DynamoDBTableName",
            value=users_table.table_name,
            description="DynamoDB table name",
            export_name="AI-DJ-DynamoDB-Table",
        )

        CfnOutput(
            self,
            "LambdaFunctionName",
            value=lambda_function.function_name,
            description="Lambda function name",
            export_name="AI-DJ-Lambda-Function",
        )
        
        CfnOutput(
            self,
            "AgentEndpoint",
            value=f"{http_api.url}agent/chat",
            description="AgentCore conversational endpoint",
        )
        
        CfnOutput(
            self,
            "ImageEndpoint",
            value=f"{http_api.url}playlist-from-image",
            description="Nova Act image-based playlist endpoint",
        )
        
        CfnOutput(
            self,
            "KnowledgeEndpoint",
            value=f"{http_api.url}music-knowledge",
            description="Amazon Q music knowledge endpoint",
        )

        # ========================================
        # S3 Bucket for Frontend
        # ========================================
        frontend_bucket = s3.Bucket(
            self,
            "FrontendBucket",
            website_index_document="index.html",
            website_error_document="index.html",
            public_read_access=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            ),
        )

        # Deploy frontend files
        s3deploy.BucketDeployment(
            self,
            "DeployFrontend",
            sources=[s3deploy.Source.asset("./frontend")],
            destination_bucket=frontend_bucket,
        )

        # ========================================
        # CloudFront Distribution
        # ========================================
        distribution = cloudfront.Distribution(
            self,
            "FrontendDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(frontend_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                compress=True,
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(5),
                )
            ],
        )

        CfnOutput(
            self,
            "FrontendURL",
            value=f"https://{distribution.distribution_domain_name}",
            description="Frontend CloudFront URL (HTTPS)",
            export_name="AI-DJ-Frontend-URL",
        )

        CfnOutput(
            self,
            "SpotifyRedirectURI",
            value=f"https://{distribution.distribution_domain_name}/",
            description="Add this to Spotify Redirect URIs",
        )

        # ========================================
        # Spotify OAuth Callback Lambda
        # ========================================
        oauth_lambda = _lambda.Function(
            self,
            "SpotifyOAuthHandler",
            function_name="Spotify-OAuth-Handler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="auth.lambda_handler",
            code=_lambda.Code.from_asset("spotify_auth"),
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "SPOTIFY_CLIENT_ID": spotify_client_id,
                "SPOTIFY_CLIENT_SECRET": spotify_client_secret,
                "REDIRECT_URI": f"{http_api.url}callback",
                "FRONTEND_URL": f"https://{distribution.distribution_domain_name}",
            },
        )

        # Add OAuth callback route to API Gateway
        oauth_integration = integrations.HttpLambdaIntegration(
            "SpotifyOAuthIntegration",
            oauth_lambda,
        )

        http_api.add_routes(
            path="/callback",
            methods=[apigw.HttpMethod.GET],
            integration=oauth_integration,
        )

        CfnOutput(
            self,
            "OAuthCallbackURL",
            value=f"{http_api.url}callback",
            description="OAuth Callback URL for Spotify",
        )
