"""
generate_data.py
-----------------
Generates a realistic sample sales/customer dataset used by the KPI Dashboard.
Run this once if you ever want to regenerate data/sales_data.csv with new
random values:

    python generate_data.py

The dashboard (app.py) already ships with a pre-generated CSV, so running
this script is OPTIONAL.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

REGIONS = ["North", "South", "East", "West", "Central"]
CATEGORIES = ["Electronics", "Apparel", "Home & Kitchen", "Sports", "Beauty"]
PRODUCTS = {
    "Electronics": ["Wireless Earbuds", "Smartwatch", "Bluetooth Speaker", "Laptop Stand"],
    "Apparel": ["T-Shirt", "Denim Jacket", "Sneakers", "Hoodie"],
    "Home & Kitchen": ["Air Fryer", "Blender", "Cookware Set", "Vacuum Cleaner"],
    "Sports": ["Yoga Mat", "Dumbbell Set", "Running Shoes", "Cycling Helmet"],
    "Beauty": ["Face Serum", "Lipstick", "Hair Dryer", "Perfume"],
}

POSITIVE_FEEDBACK = [
    "I absolutely love this product, works perfectly!",
    "Great quality and fast delivery, highly recommend.",
    "Excellent value for money, will buy again.",
    "Amazing experience, customer service was fantastic.",
    "Superb build quality, exceeded my expectations.",
    "Very satisfied with the purchase, five stars.",
]
NEUTRAL_FEEDBACK = [
    "The product is okay, does what it says.",
    "It's an average product, nothing special.",
    "Delivery was on time, product is fine.",
    "Decent quality for the price point.",
]
NEGATIVE_FEEDBACK = [
    "Very disappointed, the product broke in a week.",
    "Poor quality, would not recommend this to anyone.",
    "Terrible experience, delivery was late and item was damaged.",
    "Not worth the money, quite unhappy with this purchase.",
    "Bad customer support and low quality product.",
]

def random_feedback():
    r = np.random.rand()
    if r < 0.55:
        return np.random.choice(POSITIVE_FEEDBACK)
    elif r < 0.80:
        return np.random.choice(NEUTRAL_FEEDBACK)
    else:
        return np.random.choice(NEGATIVE_FEEDBACK)

def generate(n_rows=1500, start_date="2024-01-01", end_date="2025-12-31"):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    date_range_days = (end - start).days

    rows = []
    n_customers = 400
    customer_ids = [f"CUST{str(i).zfill(4)}" for i in range(1, n_customers + 1)]

    # Give each customer a "first seen" day so customer growth trends look organic
    customer_first_seen = {
        cid: np.random.randint(0, date_range_days) for cid in customer_ids
    }

    for i in range(n_rows):
        region = np.random.choice(REGIONS)
        category = np.random.choice(CATEGORIES)
        product = np.random.choice(PRODUCTS[category])

        customer = np.random.choice(customer_ids)
        min_day = customer_first_seen[customer]
        day_offset = np.random.randint(min_day, date_range_days) if min_day < date_range_days else min_day
        order_date = start + timedelta(days=int(day_offset))

        quantity = np.random.randint(1, 6)
        unit_price = round(np.random.uniform(10, 500), 2)
        revenue = round(quantity * unit_price, 2)
        cost_ratio = np.random.uniform(0.45, 0.75)
        cost = round(revenue * cost_ratio, 2)
        profit = round(revenue - cost, 2)

        rows.append({
            "order_id": f"ORD{str(i+1).zfill(5)}",
            "order_date": order_date.strftime("%Y-%m-%d"),
            "customer_id": customer,
            "region": region,
            "category": category,
            "product": product,
            "quantity": quantity,
            "unit_price": unit_price,
            "revenue": revenue,
            "cost": cost,
            "profit": profit,
            "customer_feedback": random_feedback(),
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("order_date").reset_index(drop=True)
    return df

if __name__ == "__main__":
    df = generate()
    df.to_csv("data/sales_data.csv", index=False)
    print(f"Generated {len(df)} rows -> data/sales_data.csv")
