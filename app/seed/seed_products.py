import uuid
import boto3
from datetime import datetime, timezone
from app.core.config import TABLE_NAME, AWS_REGION

SAMPLE_PRODUCTS = [
    {"name": "Wireless Bluetooth Headphones", "description": "Noise-cancelling over-ear headphones with 30h battery", "category": "electronics", "price": "79.99", "stock": 150, "image_url": ""},
    {"name": "USB-C Charging Cable 2m", "description": "Braided fast charging cable compatible with most devices", "category": "electronics", "price": "12.99", "stock": 500, "image_url": ""},
    {"name": "Mechanical Keyboard RGB", "description": "Full-size mechanical keyboard with Cherry MX switches", "category": "electronics", "price": "129.99", "stock": 75, "image_url": ""},
    {"name": "Smartphone Stand Adjustable", "description": "Aluminum adjustable phone and tablet stand", "category": "electronics", "price": "24.99", "stock": 200, "image_url": ""},
    {"name": "Cotton T-Shirt Black", "description": "100% organic cotton crew neck t-shirt", "category": "clothing", "price": "19.99", "stock": 300, "image_url": ""},
    {"name": "Running Shoes Pro", "description": "Lightweight running shoes with cushioned sole", "category": "clothing", "price": "89.99", "stock": 80, "image_url": ""},
    {"name": "Denim Jacket Classic", "description": "Classic fit denim jacket with button closure", "category": "clothing", "price": "59.99", "stock": 60, "image_url": ""},
    {"name": "Wool Winter Beanie", "description": "Warm knitted beanie for cold weather", "category": "clothing", "price": "14.99", "stock": 250, "image_url": ""},
    {"name": "Stainless Steel Water Bottle", "description": "Insulated 750ml water bottle keeps drinks cold 24h", "category": "home", "price": "29.99", "stock": 180, "image_url": ""},
    {"name": "LED Desk Lamp", "description": "Adjustable LED desk lamp with 3 brightness levels", "category": "home", "price": "34.99", "stock": 120, "image_url": ""},
    {"name": "Ceramic Coffee Mug Set", "description": "Set of 4 handmade ceramic mugs 350ml each", "category": "home", "price": "39.99", "stock": 90, "image_url": ""},
    {"name": "Yoga Mat Premium", "description": "Non-slip 6mm thick yoga mat with carrying strap", "category": "sports", "price": "44.99", "stock": 100, "image_url": ""},
    {"name": "Resistance Bands Set", "description": "Set of 5 resistance bands with different strengths", "category": "sports", "price": "22.99", "stock": 200, "image_url": ""},
    {"name": "Football Official Size", "description": "FIFA approved match football size 5", "category": "sports", "price": "34.99", "stock": 70, "image_url": ""},
    {"name": "Python Programming Book", "description": "Complete guide to Python programming for beginners", "category": "books", "price": "42.99", "stock": 50, "image_url": ""},
    {"name": "Science Fiction Novel Collection", "description": "Box set of 5 classic sci-fi novels", "category": "books", "price": "54.99", "stock": 40, "image_url": ""},
    {"name": "Building Blocks 500pc", "description": "Creative building blocks set for ages 6+", "category": "toys", "price": "29.99", "stock": 110, "image_url": ""},
    {"name": "Remote Control Car", "description": "Off-road RC car with rechargeable battery", "category": "toys", "price": "49.99", "stock": 65, "image_url": ""},
    {"name": "Organic Green Tea Box", "description": "20 sachets of premium organic green tea", "category": "food", "price": "9.99", "stock": 400, "image_url": ""},
    {"name": "Dark Chocolate Assortment", "description": "Gift box with 12 artisan dark chocolate pieces", "category": "food", "price": "24.99", "stock": 150, "image_url": ""},
    {"name": "Moisturizing Face Cream", "description": "Natural ingredients face cream for all skin types", "category": "beauty", "price": "18.99", "stock": 0, "image_url": ""},
    {"name": "Garden Tool Set", "description": "5-piece stainless steel garden tool set with bag", "category": "garden", "price": "37.99", "stock": 85, "image_url": ""},
    {"name": "Car Phone Mount", "description": "Universal magnetic car phone holder for dashboard", "category": "automotive", "price": "15.99", "stock": 300, "image_url": ""},
    {"name": "Portable Bluetooth Speaker", "description": "Waterproof portable speaker with 12h battery life", "category": "electronics", "price": "49.99", "stock": 0, "image_url": ""},
]


def seed():
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    table = dynamodb.Table(TABLE_NAME)

    now = datetime.now(timezone.utc).isoformat()

    with table.batch_writer() as batch:
        for product_data in SAMPLE_PRODUCTS:
            item = {
                "id": str(uuid.uuid4()),
                "name": product_data["name"],
                "description": product_data["description"],
                "category": product_data["category"],
                "price": product_data["price"],
                "stock": product_data["stock"],
                "available": product_data["stock"] > 0,
                "image_url": product_data["image_url"],
                "created_at": now,
            }
            batch.put_item(Item=item)

    print(f"Seeded {len(SAMPLE_PRODUCTS)} products into table '{TABLE_NAME}'")


if __name__ == "__main__":
    seed()
