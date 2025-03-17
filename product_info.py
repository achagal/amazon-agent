import requests
import datetime
import json
import os
from dotenv import load_dotenv
import time  # Add this at the top with other imports

# Load environment variables
load_dotenv()

# Get credentials from environment variables
access_token = os.getenv('AMAZON_ACCESS_TOKEN')
marketplace_id = os.getenv('AMAZON_MARKETPLACE_ID')
asin = 'B081ZZZYYM'
region = 'us-east-1'  # Example region
endpoint = 'https://sellingpartnerapi-na.amazon.com'  # Example endpoint for North America

# Headers for SP-API request
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {access_token}',
    'x-amz-access-token': access_token
}

# Add rate limiting helper function
def rate_limit_wait():
    """Wait 2 seconds between API calls to respect rate limits"""
    time.sleep(2)

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
    
# Function to get Buy Box Competition using getPricing API
def get_buy_box_competition(asin):
    url = f"{endpoint}/catalog/2022-04-01/items/{asin}/pricing"  # Updated endpoint
    params = {
        'MarketplaceId': marketplace_id,
        'ItemType': 'Asin'  # Added required parameter
    }
    print(f"\nDebug - Buy Box API Call:")
    print(f"URL: {url}")
    print(f"Params: {params}")
    print(f"Headers: {headers}")
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        buy_box_winner = None
        competitive_offers = []

        # Updated response parsing based on new API structure
        if 'price' in data:
            buy_box_winner = data['price'].get('BuyBoxPrice')
            competitive_offers = data['price'].get('CompetitivePrice', [])

        return {
            'buy_box_winner': buy_box_winner,
            'competitive_offers': competitive_offers
        }
    else:
        print(f"Error fetching Buy Box Competition: {response.status_code}")
        print(f"Response body: {response.text}")
        return None

# Function to get New 3rd Party FBA Offers using getCompetitivePricing API
def get_new_3p_fba_offers(asin):
    url = f"{endpoint}/catalog/2022-04-01/items/{asin}/offers"  # Updated endpoint
    params = {
        'MarketplaceId': marketplace_id,
        'ItemCondition': 'New',
        'ItemType': 'Asin'  # Added required parameter
    }
    print(f"\nDebug - 3P FBA API Call:")
    print(f"URL: {url}")
    print(f"Params: {params}")
    print(f"Headers: {headers}")
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        fba_offers = []

        # Updated response parsing based on new API structure
        for offer in data.get('offers', []):
            if offer.get('fulfillmentType') == 'AFN':  # AFN means FBA
                fba_offers.append(offer)

        return {
            'fba_offers': fba_offers,
            'count': len(fba_offers)
        }
    else:
        print(f"Error fetching 3P FBA Offers: {response.status_code}")
        print(f"Response body: {response.text}")
        return None

# Function to get New Offer Count using getCompetitivePricing API
def get_new_offer_count(asin):
    url = f"{endpoint}/catalog/2022-04-01/items/{asin}/offers/summary"  # Updated endpoint
    params = {
        'MarketplaceId': marketplace_id,
        'ItemCondition': 'New',
        'ItemType': 'Asin'  # Added required parameter
    }
    print(f"\nDebug - Offer Count API Call:")
    print(f"URL: {url}")
    print(f"Params: {params}")
    print(f"Headers: {headers}")
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        # Updated response parsing based on new API structure
        offer_count = data.get('summary', {}).get('totalOfferCount', 0)

        return {
            'offer_count': offer_count
        }
    else:
        print(f"Error fetching New Offer Count: {response.status_code}")
        print(f"Response body: {response.text}")
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
print("\n=== Sales Rank ===")
sales_rank = get_sales_rank(asin)
if sales_rank:
    print("\nProduct Rankings and Price:")
    print(f"Price: {sales_rank['price']}")
    print("\nSales Rankings by Category:")
    for category, rank in sales_rank['sales_ranks'].items():
        print(f"Category {category}: #{rank:,}")

rate_limit_wait()  # Wait before next API call

# Test Buy Box Competition
print("\n=== Buy Box Competition ===")
buy_box_data = get_buy_box_competition(asin)
if buy_box_data:
    print("\nBuy Box Winner:")
    print(json.dumps(buy_box_data['buy_box_winner'], indent=2))
    print("\nCompetitive Offers:")
    print(json.dumps(buy_box_data['competitive_offers'], indent=2))

rate_limit_wait()  # Wait before next API call

# Test New 3P FBA Offers
print("\n=== New 3P FBA Offers ===")
fba_data = get_new_3p_fba_offers(asin)
if fba_data:
    print(f"\nNumber of FBA Offers: {fba_data['count']}")
    print("\nFBA Offer Details:")
    print(json.dumps(fba_data['fba_offers'], indent=2))

rate_limit_wait()  # Wait before next API call

# Test New Offer Count
print("\n=== Total New Offer Count ===")
offer_count = get_new_offer_count(asin)
if offer_count:
    print(f"\nTotal Number of Offers: {offer_count['offer_count']}")

# Note: Implement the get_product_reviews function using the Product Advertising API
