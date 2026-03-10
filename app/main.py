import os
import time

import boto3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.api.products_routes import router as products_router
from app.core.config import TABLE_NAME, AWS_REGION

_start_time = time.time()


def _check_dynamodb() -> dict:
    """Ping DynamoDB table to verify connectivity."""
    try:
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
        table = dynamodb.Table(TABLE_NAME)
        table.table_status  # forces a DescribeTable call
        return {"dynamodb": "connected", "table": TABLE_NAME, "region": AWS_REGION}
    except Exception as exc:
        return {"dynamodb": "error", "detail": str(exc)}


def create_app() -> FastAPI:
    app = FastAPI(title="Products Service", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://team2-ecommerce-frontend.s3-website-us-east-1.amazonaws.com",
        ],
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    @app.get("/", tags=["health"])
    def health_check():
        uptime_seconds = round(time.time() - _start_time, 2)
        db_status = _check_dynamodb()
        healthy = db_status.get("dynamodb") == "connected"

        return {
            "status": "healthy" if healthy else "degraded",
            "service": "products-api",
            "version": os.getenv("IMAGE_TAG", "local"),
            "environment": os.getenv("ENV", "development"),
            "region": AWS_REGION,
            "uptime_seconds": uptime_seconds,
            "dependencies": {
                "dynamodb": db_status,
            },
        }

    app.include_router(products_router)
    return app


app = create_app()

# Lambda handler expected by the AWS base image / Dockerfile (app.main.handler)
handler = Mangum(app)
