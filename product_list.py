import product_info
import pandas as pd



product_list = [] # ASIN --> product name
good_products = []


# extracts all relevant info from the csv
def extract_asins(file_path):
    """
    Reads a CSV file and extracts ASINs from it.
    
    :param file_path: Path to the CSV file.
    :return: List of ASINs.
    """
    df = pd.read_csv(file_path)
    asins = df['ASIN'].tolist()
    return asins


# determines is product is viable sell based on metrics keepa api
def make_sell_list():
    # product will be an ASIN
    for product in product_list:
        # call function from product_info that will 
        # take in the ASIN and return in a json all the metrics about it
        # given those metrics, determine
        is_good = is_good_product(product)
        if is_good:
            good_products.append(product)


def is_good_product(product):
    # given the json, determine if the product is good to sell
    # return true if it is, false otherwise

    return True


product_list = extract_asins('product-leads.csv')
print(product_list)



