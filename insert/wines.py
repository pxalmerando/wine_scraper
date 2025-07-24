import pandas as pd
import os
from typing import List, Dict

def combine_columns_A_to_F(input_dir: str = "../Input") -> Dict[str, List[str]]:
    """
    Processes all CSV/Excel files in Input folder and combines columns A-F with spaces
    
    Args:
        input_dir: Path to Input folder (default: ../Input)
    
    Returns:
        Dictionary with {filename: list_of_combined_terms}
    """
    results = {}
    
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    for filename in os.listdir(input_dir):
        filepath = os.path.join(input_dir, filename)
        
        if not (filename.endswith('.csv') or filename.endswith(('.xlsx', '.xls'))):
            continue
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
            
            # Get 1-6 columns (A-F)
            cols = df.columns[:6]
            
            combined_terms = df[cols].apply(
                lambda row: ' '.join(str(val) for val in row if pd.notna(val)), 
                axis=1
            ).tolist()
            
            results[filename] = combined_terms
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue
    
    return results

# # Usage example
# if __name__ == "__main__":
#     combined_data = combine_columns_A_to_F()
    
#     # Print results
#     for filename, terms in combined_data.items():
#         print(f"\nFile: {filename}")
#         for i, term in enumerate(terms, 1):
#             print(f"Row {i}: {term}")