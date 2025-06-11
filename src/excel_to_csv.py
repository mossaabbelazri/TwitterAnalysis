import pandas as pd
import os

def convert_excel_to_csv():
    # Read the Excel file
    excel_file = 'FabrizioRomano_tweets.xlsx'
    df = pd.read_excel(excel_file)
    
    # Create output directory if it doesn't exist
    output_dir = 'tweets'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save as CSV
    output_file = os.path.join(output_dir, 'fabrizio_romano_tweets.csv')
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Successfully converted {excel_file} to {output_file}")

if __name__ == "__main__":
    convert_excel_to_csv() 