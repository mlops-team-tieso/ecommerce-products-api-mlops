import os

TABLE_NAME = os.getenv("DYNAMODB_TABLE", "products")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
