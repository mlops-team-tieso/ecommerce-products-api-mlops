import boto3
from boto3.dynamodb.conditions import Attr
from app.core.config import TABLE_NAME, AWS_REGION


def _get_table():
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    return dynamodb.Table(TABLE_NAME)


def get_all(category=None, min_price=None, max_price=None, available=None):
    table = _get_table()
    filter_expression = None

    if category:
        condition = Attr("category").eq(category)
        filter_expression = condition if filter_expression is None else filter_expression & condition

    if min_price is not None:
        condition = Attr("price").gte(str(min_price))
        filter_expression = condition if filter_expression is None else filter_expression & condition

    if max_price is not None:
        condition = Attr("price").lte(str(max_price))
        filter_expression = condition if filter_expression is None else filter_expression & condition

    if available is not None:
        condition = Attr("available").eq(available)
        filter_expression = condition if filter_expression is None else filter_expression & condition

    scan_kwargs = {}
    if filter_expression is not None:
        scan_kwargs["FilterExpression"] = filter_expression

    response = table.scan(**scan_kwargs)
    return response.get("Items", [])


def get_by_id(product_id: str):
    table = _get_table()
    response = table.get_item(Key={"productID": product_id})
    return response.get("Item")


def create(product: dict):
    table = _get_table()
    table.put_item(Item=product)
    return product


def update(product_id: str, data: dict):
    table = _get_table()

    update_parts = []
    expression_values = {}
    expression_names = {}

    for key, value in data.items():
        safe_key = f"#{key}"
        expression_names[safe_key] = key
        expression_values[f":{key}"] = value
        update_parts.append(f"{safe_key} = :{key}")

    response = table.update_item(
        Key={"productID": product_id},
        UpdateExpression="SET " + ", ".join(update_parts),
        ExpressionAttributeValues=expression_values,
        ExpressionAttributeNames=expression_names,
        ReturnValues="ALL_NEW",
    )
    return response.get("Attributes")


def update_stock(product_id: str, stock: int):
    table = _get_table()
    available = stock > 0
    response = table.update_item(
        Key={"productID": product_id},
        UpdateExpression="SET #stock = :stock, #available = :available",
        ExpressionAttributeNames={"#stock": "stock", "#available": "available"},
        ExpressionAttributeValues={":stock": stock, ":available": available},
        ReturnValues="ALL_NEW",
    )
    return response.get("Attributes")
