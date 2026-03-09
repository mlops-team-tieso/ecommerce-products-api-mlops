import os
import pytest
import boto3
from moto import mock_aws


@pytest.fixture(autouse=True)
def aws_environment(monkeypatch):
    """Set up fake AWS credentials and table name for all tests."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-2")
    monkeypatch.setenv("DYNAMODB_TABLE", "products")
    monkeypatch.setenv("AWS_REGION", "us-east-2")


@pytest.fixture
def dynamodb_table():
    """Create a real DynamoDB table in moto's simulated environment."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-2")
        table = dynamodb.create_table(
            TableName="products",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        yield table
