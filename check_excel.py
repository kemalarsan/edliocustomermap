import pandas as pd

# Read both Excel files
charter_df = pd.read_excel('MAP - Charter & Private Clients Address-2025-07-03-08-26-15.xlsx')
district_df = pd.read_excel('MAP - District Client Address-2025-07-03-08-26-06.xlsx')

print("Charter/Private Excel columns:")
print(charter_df.columns.tolist())
print(f"\nFirst few rows:")
print(charter_df.head())

print("\n" + "="*50 + "\n")

print("District Excel columns:")
print(district_df.columns.tolist())
print(f"\nFirst few rows:")
print(district_df.head())