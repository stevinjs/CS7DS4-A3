import pandas as pd
from data.loader import get_all_data

print("--- DEBUG SCRIPT START ---")
try:
    df = get_all_data()
    print("DataFrame Info:")
    print(df.info())
    print("\nHead:")
    df.to_csv('data/debug_data_head.csv', index=True)
    print("\nIndex Type:", type(df.index))
    print("\nIndex Dtype:", df.index.dtype)
    print("\nMin Index:", df.index.min(), "Type:", type(df.index.min()))
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
print("--- DEBUG SCRIPT END ---")
