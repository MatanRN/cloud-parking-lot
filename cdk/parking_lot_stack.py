"""
Parking Lot Stack

Defines the AWS CDK stack for the serverless parking lot management system.
"""

import os

from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_apigatewayv2 as apigw
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_lambda as lambda_
from aws_cdk.aws_apigatewayv2_integrations import HttpLambdaIntegration
from constructs import Construct


class ParkingLotStack(Stack):
    """
    AWS CDK Stack for the Parking Lot Management System.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB Table for storing tickets
        ticket_table = dynamodb.Table(
            self,
            "Ticket",
            partition_key=dynamodb.Attribute(
                name="ticketId", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Define index name as a variable
        plate_index_name = "PlateStatusIndex"

        # Add GSI for searching by plate and status
        ticket_table.add_global_secondary_index(
            index_name=plate_index_name,
            partition_key=dynamodb.Attribute(
                name="plate", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="status", type=dynamodb.AttributeType.STRING
            ),
        )

        # Get the correct path to handlers directory (one level up from cdk directory)
        this_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(this_dir)
        handlers_path = os.path.join(project_dir, "handlers")

        # Create Lambda functions
        entry_fn = lambda_.Function(
            self,
            "EntryFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="entry.handler",
            code=lambda_.Code.from_asset(handlers_path),
            environment={
                "TICKET_TABLE": ticket_table.table_name,
                "PLATE_INDEX": plate_index_name,
            },
        )

        exit_fn = lambda_.Function(
            self,
            "ExitFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="exit.handler",
            code=lambda_.Code.from_asset(handlers_path),
            environment={
                "TICKET_TABLE": ticket_table.table_name,
                "PLATE_INDEX": plate_index_name,
            },
        )

        # Grant DynamoDB permissions to Lambda functions
        ticket_table.grant_read_write_data(entry_fn)
        ticket_table.grant_read_write_data(exit_fn)

        # Create API Gateway HTTP API
        api = apigw.HttpApi(self, "ParkingLotApi", api_name="parking-lot-api")

        # Add routes
        api.add_routes(
            path="/entry",
            methods=[apigw.HttpMethod.POST],
            integration=HttpLambdaIntegration("EntryIntegration", entry_fn),
        )

        api.add_routes(
            path="/exit",
            methods=[apigw.HttpMethod.POST],
            integration=HttpLambdaIntegration("ExitIntegration", exit_fn),
        )
