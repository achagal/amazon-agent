import keepa
import datetime
import calendar
from collections import defaultdict

# Replace this with your actual Keepa API key
API_KEY = "2novnmm0men9k7i0l1it5j63ig4dum40rjov04fvo9o88f19997f9bnglrt7ojdn"

def get_monthly_sales_rank(asin, months=12):
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

# Example usage
asin = "B0BWSJK9DC"
monthly_data = get_monthly_sales_rank(asin)
print(monthly_data)

