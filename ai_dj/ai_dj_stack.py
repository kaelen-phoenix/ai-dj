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
        # Lambda Function
        # ========================================
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
                "BEDROCK_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
            },
        )

        # ========================================
        # IAM Permissions
        # ========================================
        
        # Permissions for DynamoDB
        users_table.grant_read_write_data(lambda_function)

        # Permissions for Amazon Bedrock
        lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=[
                    f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
                ],
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
                allow_methods=[apigw.CorsHttpMethod.POST, apigw.CorsHttpMethod.OPTIONS],
                allow_headers=["Content-Type", "Authorization"],
            ),
        )

        # Lambda Integration
        lambda_integration = integrations.HttpLambdaIntegration(
            "LambdaIntegration",
            lambda_function,
        )

        # POST /playlist route
        http_api.add_routes(
            path="/playlist",
            methods=[apigw.HttpMethod.POST],
            integration=lambda_integration,
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
