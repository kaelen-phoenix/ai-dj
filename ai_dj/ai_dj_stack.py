from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_apigatewayv2 as apigw,
    aws_apigatewayv2_integrations as integrations,
    aws_iam as iam,
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
        # Lambda Function
        # ========================================
        lambda_function = _lambda.Function(
            self,
            "AI-DJ-Handler",
            function_name="AI-DJ-Handler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="app.lambda_handler",
            code=_lambda.Code.from_asset("lambda_src"),
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
