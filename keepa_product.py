import keepa
import datetime
import calendar
from collections import defaultdict
import numpy as np

# Replace this with your actual Keepa API key
API_KEY = "2novnmm0men9k7i0l1it5j63ig4dum40rjov04fvo9o88f19997f9bnglrt7ojdn"

def get_monthly_sales_rank(asin, months=12): # *** is there in issue if product hasnt been around for 12 months?
    """
    Get monthly sales rank data for the past specified number of months.
    
    Args:
        asin: Amazon ASIN (string or list)
        months: Number of months of history to retrieve (default: 12)
        
    Returns:
        Dictionary with monthly average sales ranks
    """
    # Initialize Keepa API
    api = keepa.Keepa(API_KEY)
    
    # Print initial token information
    print(f"Initial tokens left: {api.tokens_left}")
    
    # Ensure asin is a list
    if isinstance(asin, str):
        asin = [asin]
    
    print(f"Requesting data for ASIN(s): {asin}")

    try:
        # Query the API with appropriate parameters
        products = api.query(
            asin,
            domain="US",
            history=True,
            update=1
        )

        if not products:
            print(f"No data found for ASIN: {asin}")
            return None

        product = products[0]
        print(f"Product title: {product.get('title', 'No title available')}")
        
        # Extract sales rank history
        if "data" in product and "SALES" in product["data"]:
            sales_rank_history = product["data"]["SALES"]
            timestamps = product["data"]["SALES_time"]
            
            # Create a dictionary to store monthly data
            monthly_data = defaultdict(list)
            
            # Process timestamps and sales ranks
            for i, timestamp in enumerate(timestamps):
                # Handle both datetime objects and integer timestamps
                if isinstance(timestamp, datetime.datetime):
                    date = timestamp
                else:
                    # Convert minutes since epoch to datetime if needed
                    date = datetime.datetime(1970, 1, 1) + datetime.timedelta(minutes=timestamp)
                
                # Create a month-year key (e.g., "2023-01" for January 2023)
                month_key = f"{date.year}-{date.month:02d}"
                
                # Add the sales rank to the appropriate month
                monthly_data[month_key].append(sales_rank_history[i])
            
            # Calculate monthly averages
            monthly_averages = {}
            for month, ranks in monthly_data.items():
                # Calculate average sales rank for the month
                avg_rank = sum(ranks) / len(ranks)
                monthly_averages[month] = int(avg_rank)
            
            # Sort by date (keys are in YYYY-MM format so string sorting works)
            sorted_months = sorted(monthly_averages.keys())
            
            # Get only the most recent X months
            recent_months = sorted_months[-months:] if len(sorted_months) > months else sorted_months
            
            # Create the final result dictionary with month names
            result = {}
            for month_key in recent_months:
                year, month = map(int, month_key.split('-'))
                month_name = f"{calendar.month_name[month]} {year}"
                result[month_name] = monthly_averages[month_key]
            
            print(f"Monthly average sales ranks for the past {len(result)} months:")
            for month, rank in result.items():
                print(f"{month}: {rank}")
                
            return result
        
        else:
            print(f"No sales rank data available for ASIN: {asin}")
            print(f"Available data keys: {list(product.get('data', {}).keys())}")
            return None

    except Exception as e:
        print(f"Keepa Request Error: {e}")
        print(f"Current tokens left: {api.tokens_left}")
        print(f"Error type: {type(e).__name__}")
        return None

def get_review_count_history(asin, months=12):
    """
    Get review count history and analyze its growth trend.
    
    Args:
        asin: Amazon ASIN (string or list)
        months: Number of months of history to analyze (default: 12)
        
    Returns:
        Dictionary with monthly review counts and growth metrics
    """
    # Initialize Keepa API
    api = keepa.Keepa(API_KEY)
    
    print(f"Initial tokens left: {api.tokens_left}")
    
    # Ensure asin is a list
    if isinstance(asin, str):
        asin = [asin]
    
    print(f"Requesting review data for ASIN(s): {asin}")

    try:
        # Query the API with rating parameter to ensure we get review count history
        products = api.query(
            asin,
            domain="US",
            history=True,
            update=1,
            rating=True  # Include rating and review count history
        )

        if not products:
            print(f"No data found for ASIN: {asin}")
            return None

        product = products[0]
        print(f"Product title: {product.get('title', 'No title available')}")
        
        # Extract review count history
        if "data" in product and "COUNT_REVIEWS" in product["data"]:
            review_count_history = product["data"]["COUNT_REVIEWS"]
            timestamps = product["data"]["COUNT_REVIEWS_time"]
            
            print(f"Found {len(review_count_history)} review count data points")
            
            # Create a dictionary to store monthly data
            monthly_data = defaultdict(list)
            
            # Process timestamps and review counts
            for i, timestamp in enumerate(timestamps):
                # Skip entries with no review count (value of -1 in Keepa API)
                if review_count_history[i] == -1:
                    continue
                    
                # Handle both datetime objects and integer timestamps
                if isinstance(timestamp, datetime.datetime):
                    date = timestamp
                else:
                    # Convert minutes since epoch to datetime if needed
                    date = datetime.datetime(1970, 1, 1) + datetime.timedelta(minutes=timestamp)
                
                # Create a month-year key (e.g., "2023-01" for January 2023)
                month_key = f"{date.year}-{date.month:02d}"
                
                # Add the review count to the appropriate month
                monthly_data[month_key].append(review_count_history[i])
            
            # Get the last review count for each month (most recent)
            monthly_review_counts = {}
            for month, counts in monthly_data.items():
                # Get the last (most recent) review count for the month
                monthly_review_counts[month] = counts[-1]
            
            # Sort by date
            sorted_months = sorted(monthly_review_counts.keys())
            
            # Get only the most recent X months
            recent_months = sorted_months[-months:] if len(sorted_months) > months else sorted_months
            
            # Create the final result dictionary with month names and calculate growth
            result = {
                "monthly_counts": {},
                "growth_metrics": {}
            }
            
            # Process monthly counts
            previous_count = None
            for month_key in recent_months:
                year, month = map(int, month_key.split('-'))
                month_name = f"{calendar.month_name[month]} {year}"
                count = monthly_review_counts[month_key]
                
                result["monthly_counts"][month_name] = count
                
                # Calculate month-over-month growth
                if previous_count is not None and previous_count > 0:
                    growth = count - previous_count
                    growth_percent = (growth / previous_count) * 100 if previous_count > 0 else 0
                    result["growth_metrics"][month_name] = {
                        "absolute_growth": growth,
                        "percent_growth": round(growth_percent, 2)
                    }
                
                previous_count = count
            
            # Calculate overall trend
            if len(recent_months) >= 2:
                first_month = recent_months[0]
                last_month = recent_months[-1]
                first_count = monthly_review_counts[first_month]
                last_count = monthly_review_counts[last_month]
                
                total_growth = last_count - first_count
                months_elapsed = len(recent_months) - 1
                
                # Calculate average monthly growth
                avg_monthly_growth = total_growth / months_elapsed if months_elapsed > 0 else 0
                
                # Calculate compound monthly growth rate
                if first_count > 0 and months_elapsed > 0:
                    cagr = ((last_count / first_count) ** (1 / months_elapsed)) - 1
                    cagr_percent = cagr * 100
                else:
                    cagr_percent = 0
                
                result["growth_metrics"]["overall"] = {
                    "total_growth": total_growth,
                    "avg_monthly_growth": round(avg_monthly_growth, 2),
                    "avg_monthly_growth_percent": round(cagr_percent, 2)
                }
                
                # Determine if reviews are steadily increasing
                is_increasing = total_growth > 0 and avg_monthly_growth > 0
                result["growth_metrics"]["is_steadily_increasing"] = is_increasing
            
            print(f"\nMonthly review counts for the past {len(result['monthly_counts'])} months:")
            for month, count in result["monthly_counts"].items():
                print(f"{month}: {count} reviews")
            
            if "overall" in result["growth_metrics"]:
                print(f"\nOverall growth metrics:")
                print(f"Total growth: {result['growth_metrics']['overall']['total_growth']} reviews")
                print(f"Average monthly growth: {result['growth_metrics']['overall']['avg_monthly_growth']} reviews")
                print(f"Average monthly growth rate: {result['growth_metrics']['overall']['avg_monthly_growth_percent']}%")
                print(f"Reviews steadily increasing: {'Yes' if result['growth_metrics']['is_steadily_increasing'] else 'No'}")
            
            return result
        
        else:
            print(f"No review count data available for ASIN: {asin}")
            print(f"Available data keys: {list(product.get('data', {}).keys())}")
            return None

    except Exception as e:
        print(f"Keepa Request Error: {e}")
        print(f"Current tokens left: {api.tokens_left}")
        print(f"Error type: {type(e).__name__}")
        return None

def get_offer_count_history(asin, months=12):
    """
    Get historical offer count data and analyze its trend.
    
    Args:
        asin: Amazon ASIN (string or list)
        months: Number of months of history to analyze (default: 12)
        
    Returns:
        Dictionary with monthly offer counts and trend metrics or None if data not available
    """
    # Initialize Keepa API
    api = keepa.Keepa(API_KEY)
    
    print(f"Initial tokens left: {api.tokens_left}")
    
    # Ensure asin is a list
    if isinstance(asin, str):
        asin = [asin]
    
    print(f"Requesting offer data for ASIN(s): {asin}")
    tokens_before = api.tokens_left

    try:
        # Query the API with offers parameter to get offer count history
        # Note: This will consume more tokens (6 per offer page found)
        products = api.query(
            asin,
            domain="US",
            history=True,
            update=1,
            offers=20  # Request up to 20 offers (minimum value allowed)
        )
        
        tokens_after = api.tokens_left
        tokens_used = tokens_before - tokens_after
        print(f"Tokens consumed for this request: {tokens_used}")

        if not products:
            print(f"No data found for ASIN: {asin}")
            return None

        product = products[0]
        print(f"Product title: {product.get('title', 'No title available')}")
        
        # Check if we have offer count data
        # Only look for the proper offer count fields
        offer_count_field = None
        timestamp_field = None
        
        # Check for different possible offer count fields
        if "data" in product:
            data_keys = product["data"].keys()
            
            # Try to find the appropriate offer count field
            if "COUNT_OFFERS_NEW" in data_keys and "COUNT_OFFERS_NEW_time" in data_keys:
                offer_count_field = "COUNT_OFFERS_NEW"
                timestamp_field = "COUNT_OFFERS_NEW_time"
            elif "COUNT_OFFERS" in data_keys and "COUNT_OFFERS_time" in data_keys:
                offer_count_field = "COUNT_OFFERS"
                timestamp_field = "COUNT_OFFERS_time"
        
        if offer_count_field and timestamp_field:
            offer_count_history = product["data"][offer_count_field]
            timestamps = product["data"][timestamp_field]
            
            print(f"Found {len(offer_count_history)} offer count data points using {offer_count_field}")
            
            # Create a dictionary to store monthly data
            monthly_data = defaultdict(list)
            
            # Process timestamps and offer counts
            for i, timestamp in enumerate(timestamps):
                # Skip entries with no offer count (value of -1 in Keepa API)
                if offer_count_history[i] == -1:
                    continue
                    
                # Handle both datetime objects and integer timestamps
                if isinstance(timestamp, datetime.datetime):
                    date = timestamp
                else:
                    # Convert minutes since epoch to datetime if needed
                    date = datetime.datetime(1970, 1, 1) + datetime.timedelta(minutes=timestamp)
                
                # Create a month-year key (e.g., "2023-01" for January 2023)
                month_key = f"{date.year}-{date.month:02d}"
                
                # Add the offer count to the appropriate month
                monthly_data[month_key].append(offer_count_history[i])
            
            # Calculate monthly averages
            monthly_offer_counts = {}
            for month, counts in monthly_data.items():
                # Calculate average offer count for the month
                avg_count = sum(counts) / len(counts)
                monthly_offer_counts[month] = round(avg_count, 1)
            
            # Sort by date
            sorted_months = sorted(monthly_offer_counts.keys())
            
            # Get only the most recent X months
            recent_months = sorted_months[-months:] if len(sorted_months) > months else sorted_months
            
            # Create the final result dictionary with month names and calculate trend
            result = {
                "monthly_counts": {},
                "trend_metrics": {}
            }
            
            # Process monthly counts
            previous_count = None
            for month_key in recent_months:
                year, month = map(int, month_key.split('-'))
                month_name = f"{calendar.month_name[month]} {year}"
                count = monthly_offer_counts[month_key]
                
                result["monthly_counts"][month_name] = count
                
                # Calculate month-over-month change
                if previous_count is not None and previous_count > 0:
                    change = count - previous_count
                    change_percent = (change / previous_count) * 100 if previous_count > 0 else 0
                    result["trend_metrics"][month_name] = {
                        "absolute_change": round(change, 1),
                        "percent_change": round(change_percent, 2)
                    }
                
                previous_count = count
            
            # Calculate overall trend
            if len(recent_months) >= 2:
                first_month = recent_months[0]
                last_month = recent_months[-1]
                first_count = monthly_offer_counts[first_month]
                last_count = monthly_offer_counts[last_month]
                
                total_change = last_count - first_count
                months_elapsed = len(recent_months) - 1
                
                # Calculate average monthly change
                avg_monthly_change = total_change / months_elapsed if months_elapsed > 0 else 0
                
                # Calculate percent change
                percent_change = (total_change / first_count) * 100 if first_count > 0 else 0
                
                result["trend_metrics"]["overall"] = {
                    "total_change": round(total_change, 1),
                    "avg_monthly_change": round(avg_monthly_change, 2),
                    "percent_change": round(percent_change, 2)
                }
                
                # Determine if offers are steadily decreasing
                is_decreasing = total_change < 0 and avg_monthly_change < 0
                result["trend_metrics"]["is_steadily_decreasing"] = is_decreasing
            
            print(f"\nMonthly average offer counts for the past {len(result['monthly_counts'])} months:")
            for month, count in result["monthly_counts"].items():
                print(f"{month}: {count} offers")
            
            if "overall" in result["trend_metrics"]:
                print(f"\nOverall trend metrics:")
                print(f"Total change: {result['trend_metrics']['overall']['total_change']} offers")
                print(f"Average monthly change: {result['trend_metrics']['overall']['avg_monthly_change']} offers")
                print(f"Percent change: {result['trend_metrics']['overall']['percent_change']}%")
                print(f"Offers steadily decreasing: {'Yes' if result['trend_metrics'].get('is_steadily_decreasing', False) else 'No'}")
            
            return result
        
        else:
            # No proper offer count data available
            print(f"No offer count data available for ASIN: {asin}")
            
            # Check if we have actual offer objects we could count
            if "offers" in product and product["offers"]:
                current_offer_count = len(product["offers"])
                print(f"Found {current_offer_count} current marketplace offers, but no historical offer count data")
            
            # List all available data keys for debugging
            available_fields = []
            if "data" in product:
                available_fields = list(product["data"].keys())
                print(f"Available data keys: {available_fields}")
            
            # Return an empty structure
            return {
                "monthly_counts": {},
                "trend_metrics": {},
                "error": "No historical offer count data available for this product"
            }

    except Exception as e:
        print(f"Keepa Request Error: {e}")
        print(f"Current tokens left: {api.tokens_left}")
        print(f"Error type: {type(e).__name__}")
        return None

# def analyze_buy_box_competition(asin, months=12):
#     """
#     Analyze Buy Box competition by tracking price and ownership changes.
    
#     Args:
#         asin: Amazon ASIN (string or list)
#         months: Number of months of history to analyze (default: 12)
        
#     Returns:
#         Dictionary with Buy Box competition metrics
#     """
#     # Initialize Keepa API
#     api = keepa.Keepa(API_KEY)
    
#     print(f"Initial tokens left: {api.tokens_left}")
    
#     # Ensure asin is a list
#     if isinstance(asin, str):
#         asin = [asin]
    
#     print(f"Requesting Buy Box data for ASIN(s): {asin}")

#     try:
#         # Query the API with necessary parameters
#         products = api.query(
#             asin,
#             domain="US",
#             history=True,
#             update=1,
#             offers=20  # Need offers data to get Buy Box information
#         )

#         if not products:
#             print(f"No data found for ASIN: {asin}")
#             return None

#         product = products[0]
#         print(f"Product title: {product.get('title', 'No title available')}")
        
#         # Check for Buy Box data fields
#         required_fields = [
#             "BUY_BOX_SHIPPING",
#             "BUY_BOX_SHIPPING_time",
#             "BUY_BOX_IS_FBA",  # Indicates if Buy Box winner is FBA
#             "BUY_BOX_IS_AMAZON"  # Indicates if Buy Box winner is Amazon
#         ]
        
#         if "data" not in product or not all(field in product["data"] for field in required_fields):
#             print("Buy Box data not available for this product")
#             return {
#                 "monthly_metrics": {},
#                 "error": "Buy Box data not available"
#             }
        
#         # Extract Buy Box history
#         bb_prices = product["data"]["BUY_BOX_SHIPPING"]
#         bb_times = product["data"]["BUY_BOX_SHIPPING_time"]
#         bb_is_fba = product["data"]["BUY_BOX_IS_FBA"]
#         bb_is_amazon = product["data"]["BUY_BOX_IS_AMAZON"]
        
#         # Create a dictionary to store monthly data
#         monthly_data = defaultdict(lambda: {
#             "price_changes": 0,
#             "seller_changes": 0,
#             "amazon_share": 0,
#             "fba_share": 0,
#             "fbm_share": 0,
#             "total_datapoints": 0,
#             "unique_prices": set(),
#             "avg_price": 0,
#             "price_volatility": 0
#         })
        
#         # Process Buy Box history
#         previous_price = None
#         previous_seller_type = None
        
#         for i in range(len(bb_times)):
#             # Skip invalid data points (-1 indicates no data)
#             if bb_prices[i] == -1:
#                 continue
                
#             # Convert timestamp to datetime
#             if isinstance(bb_times[i], datetime.datetime):
#                 date = bb_times[i]
#             else:
#                 date = datetime.datetime(1970, 1, 1) + datetime.timedelta(minutes=bb_times[i])
            
#             # Create month key
#             month_key = f"{date.year}-{date.month:02d}"
            
#             # Determine seller type
#             if bb_is_amazon[i]:
#                 seller_type = "Amazon"
#             elif bb_is_fba[i]:
#                 seller_type = "FBA"
#             else:
#                 seller_type = "FBM"
            
#             # Track price changes
#             if previous_price is not None and bb_prices[i] != previous_price:
#                 monthly_data[month_key]["price_changes"] += 1
            
#             # Track seller type changes
#             if previous_seller_type is not None and seller_type != previous_seller_type:
#                 monthly_data[month_key]["seller_changes"] += 1
            
#             # Update seller type shares
#             monthly_data[month_key]["total_datapoints"] += 1
#             if seller_type == "Amazon":
#                 monthly_data[month_key]["amazon_share"] += 1
#             elif seller_type == "FBA":
#                 monthly_data[month_key]["fba_share"] += 1
#             else:
#                 monthly_data[month_key]["fbm_share"] += 1
            
#             # Track prices
#             monthly_data[month_key]["unique_prices"].add(bb_prices[i])
            
#             # Update previous values
#             previous_price = bb_prices[i]
#             previous_seller_type = seller_type
        
#         # Calculate monthly metrics
#         result = {
#             "monthly_metrics": {},
#             "overall_metrics": {}
#         }
        
#         sorted_months = sorted(monthly_data.keys())
#         recent_months = sorted_months[-months:] if len(sorted_months) > months else sorted_months
        
#         total_changes = 0
#         total_datapoints = 0
        
#         for month_key in recent_months:
#             data = monthly_data[month_key]
#             total_points = data["total_datapoints"]
            
#             if total_points > 0:
#                 year, month = map(int, month_key.split('-'))
#                 month_name = f"{calendar.month_name[month]} {year}"
                
#                 metrics = {
#                     "price_changes": data["price_changes"],
#                     "seller_changes": data["seller_changes"],
#                     "unique_prices": len(data["unique_prices"]),
#                     "amazon_share": round(data["amazon_share"] / total_points * 100, 2),
#                     "fba_share": round(data["fba_share"] / total_points * 100, 2),
#                     "fbm_share": round(data["fbm_share"] / total_points * 100, 2),
#                     "competition_score": data["price_changes"] + data["seller_changes"]
#                 }
                
#                 result["monthly_metrics"][month_name] = metrics
#                 total_changes += metrics["competition_score"]
#                 total_datapoints += total_points
        
#         # Calculate overall metrics
#         if total_datapoints > 0:
#             result["overall_metrics"] = {
#                 "avg_monthly_changes": round(total_changes / len(recent_months), 2),
#                 "competition_level": "High" if total_changes / len(recent_months) > 10 else 
#                                    "Medium" if total_changes / len(recent_months) > 5 else 
#                                    "Low"
#             }
        
#         # Print summary
#         print("\nBuy Box Competition Analysis:")
#         print(f"Analyzed {len(result['monthly_metrics'])} months of data")
        
#         if result["monthly_metrics"]:
#             print("\nMonthly Metrics:")
#             for month, metrics in result["monthly_metrics"].items():
#                 print(f"\n{month}:")
#                 print(f"  Price Changes: {metrics['price_changes']}")
#                 print(f"  Seller Changes: {metrics['seller_changes']}")
#                 print(f"  Unique Prices: {metrics['unique_prices']}")
#                 print(f"  Amazon Share: {metrics['amazon_share']}%")
#                 print(f"  FBA Share: {metrics['fba_share']}%")
#                 print(f"  FBM Share: {metrics['fbm_share']}%")
        
#         if "overall_metrics" in result:
#             print(f"\nOverall Competition Level: {result['overall_metrics']['competition_level']}")
#             print(f"Average Monthly Changes: {result['overall_metrics']['avg_monthly_changes']}")
        
#         return result

#     except Exception as e:
#         print(f"Error analyzing Buy Box competition: {e}")
#         print(f"Error type: {type(e).__name__}")
#         return None


def analyze_price_stability(asin, months=12):
    """
    Analyze price stability across different price types (Amazon, New, Used, Buy Box).
    
    Args:
        asin: Amazon ASIN (string or list)
        months: Number of months of history to analyze (default: 12)
        
    Returns:
        Dictionary with price stability metrics for each price type
    """
    # Initialize Keepa API
    api = keepa.Keepa(API_KEY)
    
    print(f"Initial tokens left: {api.tokens_left}")
    
    # Ensure asin is a list
    if isinstance(asin, str):
        asin = [asin]
    
    print(f"Requesting price history for ASIN(s): {asin}")

    try:
        # Query the API
        products = api.query(
            asin,
            domain="US",
            history=True,
            update=1
        )

        if not products:
            print(f"No data found for ASIN: {asin}")
            return None

        product = products[0]
        print(f"Product title: {product.get('title', 'No title available')}")
        
        # Define price types to track
        price_types = {
            "AMAZON": "Amazon Direct",
            "NEW": "New 3rd Party",
            "USED": "Used",
            "BUY_BOX_SHIPPING": "Buy Box"
        }
        
        result = {
            "monthly_prices": {},
            "stability_metrics": {},
            "overall_metrics": {}
        }
        
        # Process each price type
        for price_field, price_name in price_types.items():
            if price_field not in product.get("data", {}) or f"{price_field}_time" not in product["data"]:
                print(f"No {price_name} price data available")
                continue
            
            prices = product["data"][price_field]
            timestamps = product["data"][f"{price_field}_time"]
            
            # Create a dictionary to store monthly data
            monthly_data = defaultdict(list)
            
            # Process timestamps and prices
            for i, timestamp in enumerate(timestamps):
                # Skip invalid prices (-1 indicates no data)
                if prices[i] == -1:
                    continue
                
                # Convert timestamp to datetime
                if isinstance(timestamp, datetime.datetime):
                    date = timestamp
                else:
                    date = datetime.datetime(1970, 1, 1) + datetime.timedelta(minutes=timestamp)
                
                # Create month key
                month_key = f"{date.year}-{date.month:02d}"
                
                # Add the price to the appropriate month
                # Convert price to dollars (Keepa stores prices in cents)
                monthly_data[month_key].append(prices[i] / 100)
            
            # Sort months and get recent ones
            sorted_months = sorted(monthly_data.keys())
            recent_months = sorted_months[-months:] if len(sorted_months) > months else sorted_months
            
            # Calculate monthly metrics
            price_metrics = {}
            all_prices = []
            
            for month_key in recent_months:
                month_prices = monthly_data[month_key]
                if month_prices:
                    year, month = map(int, month_key.split('-'))
                    month_name = f"{calendar.month_name[month]} {year}"
                    
                    metrics = {
                        "min_price": round(min(month_prices), 2),
                        "max_price": round(max(month_prices), 2),
                        "avg_price": round(sum(month_prices) / len(month_prices), 2),
                        "price_changes": len(set(month_prices)) - 1,
                        "volatility": round(np.std(month_prices), 2) if len(month_prices) > 1 else 0
                    }
                    
                    # Calculate price range as a percentage of average price
                    price_range = metrics["max_price"] - metrics["min_price"]
                    price_range_percent = (price_range / metrics["avg_price"]) * 100 if metrics["avg_price"] > 0 else 0
                    metrics["price_range_percent"] = round(price_range_percent, 2)
                    
                    price_metrics[month_name] = metrics
                    all_prices.extend(month_prices)
            
            if all_prices:
                # Calculate overall stability metrics
                overall_metrics = {
                    "min_price": round(min(all_prices), 2),
                    "max_price": round(max(all_prices), 2),
                    "avg_price": round(sum(all_prices) / len(all_prices), 2),
                    "total_price_changes": len(set(all_prices)) - 1,
                    "overall_volatility": round(np.std(all_prices), 2),
                }
                
                # Calculate overall price range as a percentage
                overall_range = overall_metrics["max_price"] - overall_metrics["min_price"]
                overall_range_percent = (overall_range / overall_metrics["avg_price"]) * 100 if overall_metrics["avg_price"] > 0 else 0
                overall_metrics["price_range_percent"] = round(overall_range_percent, 2)
                
                # Determine price stability level
                if overall_range_percent <= 10:
                    stability_level = "Very Stable"
                elif overall_range_percent <= 20:
                    stability_level = "Stable"
                elif overall_range_percent <= 30:
                    stability_level = "Moderately Stable"
                else:
                    stability_level = "Volatile"
                
                overall_metrics["stability_level"] = stability_level
                
                # Store results
                result["monthly_prices"][price_name] = price_metrics
                result["stability_metrics"][price_name] = overall_metrics
        
        # Print summary
        print("\nPrice Stability Analysis:")
        for price_type, metrics in result["stability_metrics"].items():
            print(f"\n{price_type} Prices:")
            print(f"Price Range: ${metrics['min_price']} - ${metrics['max_price']}")
            print(f"Average Price: ${metrics['avg_price']}")
            print(f"Price Range: {metrics['price_range_percent']}% of average price")
            print(f"Total Price Changes: {metrics['total_price_changes']}")
            print(f"Stability Level: {metrics['stability_level']}")
        
        return result

    except Exception as e:
        print(f"Error analyzing price stability: {e}")
        print(f"Error type: {type(e).__name__}")
        return None

# Example usage
asin = "B07VDW3KXW"
print("\n=== SALES RANK DATA ===")
monthly_sales_data = get_monthly_sales_rank(asin)

print("\n=== REVIEW COUNT HISTORY ===")
review_data = get_review_count_history(asin)
print(review_data)

print("\n=== OFFER COUNT HISTORY ===") # only curr offer count works, not historical
offer_data = get_offer_count_history(asin)
print(offer_data)

# print("\n=== BUY BOX COMPETITION ANALYSIS ===") # not working
# competition_data = analyze_buy_box_competition(asin)

print("\n=== PRICE STABILITY ANALYSIS ===")
price_stability = analyze_price_stability(asin)
print(price_stability)



