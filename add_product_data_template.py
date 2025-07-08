#!/usr/bin/env python3
"""
Template script for adding product data to customer records.
This script shows how to merge product information with existing geocoded data.
"""

import json
import pandas as pd

def load_customer_data():
    """Load existing customer data from data.js"""
    with open('data.js', 'r') as f:
        content = f.read()
        # Extract JSON array from JavaScript file
        start = content.find('[')
        end = content.rfind(']') + 1
        json_str = content[start:end]
        # Fix the trailing commas in JSON
        json_str = json_str.replace(',\n]', '\n]').replace(',\n}', '\n}')
        return json.loads(json_str)

def add_product_data(customers, product_df):
    """
    Add product information to customer records.
    
    Expected product_df columns:
    - School or District Name (or similar identifier)
    - CMS (boolean or Y/N)
    - Mobile App (boolean or Y/N)
    - Mass Communications (boolean or Y/N)
    - Payments (boolean or Y/N)
    """
    
    # Create a lookup dictionary from product data
    product_lookup = {}
    for _, row in product_df.iterrows():
        name = str(row['School or District Name']).strip()
        products = {
            'cms': bool(row.get('CMS', False)),
            'mobile': bool(row.get('Mobile App', False)),
            'masscomm': bool(row.get('Mass Communications', False)),
            'payments': bool(row.get('Payments', False))
        }
        product_lookup[name.lower()] = products
    
    # Add product data to customers
    updated_customers = []
    matched = 0
    unmatched = 0
    
    for customer in customers:
        customer_name_lower = customer['name'].lower().strip()
        
        # Try exact match first
        if customer_name_lower in product_lookup:
            customer['products'] = product_lookup[customer_name_lower]
            matched += 1
        else:
            # Try partial matching for close matches
            found = False
            for product_name in product_lookup:
                if (product_name in customer_name_lower or 
                    customer_name_lower in product_name):
                    customer['products'] = product_lookup[product_name]
                    matched += 1
                    found = True
                    break
            
            if not found:
                # Default to CMS only if no match found
                customer['products'] = {
                    'cms': True,
                    'mobile': False,
                    'masscomm': False,
                    'payments': False
                }
                unmatched += 1
        
        updated_customers.append(customer)
    
    print(f"Product data matching results:")
    print(f"  Matched: {matched}")
    print(f"  Unmatched (defaulted to CMS only): {unmatched}")
    
    return updated_customers

def save_updated_data(customers):
    """Save updated customer data back to data.js"""
    with open('data.js', 'w') as f:
        f.write("// Real Edlio customer data with product information\n")
        f.write("// Updated with product data\n")
        f.write(f"// Total customers: {len(customers)}\n")
        f.write("const customers = [\n")
        
        for i, customer in enumerate(customers):
            products_str = json.dumps(customer.get('products', {}))
            f.write(f'    {{ name: "{customer["name"]}", '
                   f'lat: {customer["lat"]}, '
                   f'lng: {customer["lng"]}, '
                   f'url: "{customer["url"]}", '
                   f'type: "{customer["type"]}", '
                   f'state: "{customer["state"]}", '
                   f'products: {products_str} }},\n')
        
        f.write("];\n")

def main():
    print("Product Data Integration Template")
    print("=================================")
    print("\nThis script demonstrates how to add product data to customer records.")
    print("\nExpected Excel columns for product data:")
    print("- School or District Name")
    print("- CMS (Y/N or boolean)")
    print("- Mobile App (Y/N or boolean)")
    print("- Mass Communications (Y/N or boolean)")
    print("- Payments (Y/N or boolean)")
    print("\nUsage:")
    print("1. Save your product data as 'product_data.xlsx'")
    print("2. Run: python3 add_product_data_template.py")
    
    # Example of how to use when product data is available:
    """
    # Load existing customer data
    customers = load_customer_data()
    print(f"\nLoaded {len(customers)} customers")
    
    # Load product data from Excel
    product_df = pd.read_excel('product_data.xlsx')
    print(f"Loaded {len(product_df)} product records")
    
    # Add product information
    updated_customers = add_product_data(customers, product_df)
    
    # Save updated data
    save_updated_data(updated_customers)
    print("\nData updated successfully!")
    """

if __name__ == "__main__":
    main()