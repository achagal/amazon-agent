import requests
import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from environment variables
access_token = os.getenv('AMAZON_ACCESS_TOKEN')
marketplace_id = os.getenv('AMAZON_MARKETPLACE_ID')
asin = 'B00HS5MAYY'
region = 'us-east-1'  # Example region
endpoint = 'https://sellingpartnerapi-na.amazon.com'  # Example endpoint for North America

# Headers for SP-API request
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {access_token}',
    'x-amz-access-token': access_token
}

# # Function to get competitive pricing
# def get_competitive_pricing(asin):
#     url = f'{endpoint}/products/pricing/v0/competitivePrice'
#     params = {
#         'MarketplaceId': marketplace_id,
#         'Asins': asin
#     }
#     response = requests.get(url, headers=headers, params=params)
#     if response.status_code == 200:
#         data = response.json()
#         return data
#     else:
#         print(f'Error: {response.status_code}')
#         return None

# # Function to get product reviews (requires Product Advertising API)
# def get_product_reviews(asin):
#     # This is a placeholder function. Implement using the Product Advertising API.
#     pass

# # Function to get offer count
# def get_offer_count(asin):
#     url = f'{endpoint}/products/pricing/v0/listings/{asin}/offers'
#     params = {
#         'MarketplaceId': marketplace_id,
#         'ItemCondition': 'New'
#     }
#     response = requests.get(url, headers=headers, params=params)
#     if response.status_code == 200:
#         data = response.json()
#         return data
#     else:
#         print(f'Error: {response.status_code}')
#         return None

# Function to get sales rank (requires Catalog Items API) ** this also gets the price
def get_sales_rank(asin):
    url = f'{endpoint}/catalog/v0/items/{asin}'
    params = {
        'MarketplaceId': marketplace_id
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        
        # Extract sales rank information
        sales_rankings = data.get('payload', {}).get('SalesRankings', [])
        # Extract price information from the correct location
        attribute_sets = data.get('payload', {}).get('AttributeSets', [])
        list_price = attribute_sets[0].get('ListPrice', {}).get('Amount') if attribute_sets else None
        currency = attribute_sets[0].get('ListPrice', {}).get('CurrencyCode') if attribute_sets else None
        
        # Format the response
        result = {
            'price': f"{list_price} {currency}" if list_price else "Price not available",
            'sales_ranks': {}
        }
        
        # Add each category's rank to the result
        for rank_info in sales_rankings:
            category = rank_info.get('ProductCategoryId')
            rank = rank_info.get('Rank')
            result['sales_ranks'][category] = rank
            
        return result
    else:
        print(f'Error: {response.status_code}')
        return None


# *** Functions to retrieve data from jsons returned by SP-API ***
# Retrieve competitive pricing
# competitive_pricing = get_competitive_pricing(asin)
# if competitive_pricing:
#     print(json.dumps(competitive_pricing, indent=4))

# Retrieve offer count
# offer_count = get_offer_count(asin)
# if offer_count:
#     print(json.dumps(offer_count, indent=4))

# Retrieve sales rank
sales_rank = get_sales_rank(asin)
if sales_rank:
    print("\nProduct Rankings and Price:")
    print(f"Price: {sales_rank['price']}")
    print("\nSales Rankings by Category:")
    for category, rank in sales_rank['sales_ranks'].items():
        print(f"Category {category}: #{rank:,}")

# Note: Implement the get_product_reviews function using the Product Advertising API
