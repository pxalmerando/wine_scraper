import logging
import pandas as pd
import os
from typing import List, Dict, Tuple
from urllib.parse import urlencode, quote, urlparse, urlunparse, parse_qs

logging.basicConfig(
    level=logging.DEBUG,  # or INFO, as needed
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs.txt", mode='a', encoding='utf-8'),
        logging.StreamHandler()  # Optional: also log to console
    ]
)

logger = logging.getLogger("vivino.helper")
logger.addHandler(logging.NullHandler())

def remove_all_url_parameters(url: str) -> str:
    logger.debug(f"Removing all URL parameters from: {url}")
    parsed_url = urlparse(url)
    new_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        '',
        parsed_url.fragment
    ))
    logger.debug(f"URL after removing parameters: {new_url}")
    return new_url

def vivino_build_url_vintage(base_url, vintage=None, country=None):
    """Add or replace the 'year' query param in the URL."""
    logger.debug(f"Building Vivino URL for vintage. Base: {base_url}, Vintage: {vintage}, Country: {country}")
    if country:
        base_url = vivino_replace_country_code(base_url, country)
        logger.debug(f"Base URL after country code replacement: {base_url}")
    if isinstance(base_url, tuple):
        base_url = base_url[-1] 
    parsed = urlparse(base_url)
    qs = parse_qs(parsed.query)
    if vintage: 
        qs['year'] = [str(vintage)]
        logger.debug(f"Set 'year' query param to: {vintage}")
    new_query = urlencode(qs, doseq=True)
    logger.debug(f"New query: {new_query}")
    result_url = urlunparse(parsed._replace(query=new_query))
    logger.debug(f"Final Vivino URL with vintage: {result_url}")
    return result_url

def vivino_replace_country_code(url, replace_with=None):
    logger.debug(f"Replacing country code in URL: {url} with: {replace_with}")
    url = remove_all_url_parameters(url)
    if isinstance(url, tuple):
        url = url[0]
    parsed = urlparse(url)
    path_parts = parsed.path.lstrip('/').split('/')
    if len(path_parts) > 0:
        country = path_parts[0]
        if replace_with:
            path_parts[0] = replace_with
            new_path = '/' + '/'.join(path_parts)
            new_url = urlunparse(parsed._replace(path=new_path))
            logger.debug(f"Country code replaced. New URL: {new_url}")
            return replace_with, new_url
        logger.debug(f"Extracted country code: {country}")
        return country
    logger.debug("No country code found in URL.")
    return None


def get_keyword_column_A_to_F_with_index(input_dir: str = None) -> Dict[str, List[Tuple[int, str]]]:
    """
    Processes all CSV/Excel files in Input folder and combines columns A-F with spaces,
    including the original row index.
    
    Args:
        input_dir: Path to Input folder (default: ../Input)
    
    Returns:
        Dictionary with {filename: list_of_tuples} where each tuple is (row_index, combined_terms)
    """
    results = {}
    
    if input_dir is None:
        input_dir = '../Input'
    
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
            cols = df.columns[:10]
            
            # Create list of tuples (index, combined_terms)
            combined_with_index = []
            for idx, row in df[cols].iterrows():
                # Convert row values into a tuple, replacing NaN/empty with ""
                row_tuple = tuple(
                    int(val) if isinstance(val, float) and val.is_integer()
                    else (val if pd.notna(val) else "")  # Replace NaN with ""
                    for val in row
                )
                combined_with_index.append((idx, row_tuple))  # Store (index, (val1, val2, ...))

            results[filename] = combined_with_index
                        
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue
    
    return results

def update_cell_in_file(filepath: str, row_idx: int, column, value) -> bool:
    """
    Update a specific cell in a CSV or Excel file.
    Args:
        filepath: Path to the file (CSV or Excel).
        row_idx: Zero-based row index to update.
        column: Column name (str) or index (int) to update.
        value: Value to insert.
    Returns:
        True if update is successful, False otherwise.
    """
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filepath)
        else:
            logger.error(f"Unsupported file type: {filepath}")
            return False

        # If column is an int, get the column name
        if isinstance(column, int):
            if column < 0 or column >= len(df.columns):
                logger.error(f"Column index {column} out of range for {filepath}")
                return False
            column = df.columns[column]

        if row_idx < 0 or row_idx >= len(df):
            logger.error(f"Row index {row_idx} out of range for {filepath}")
            return False

        df.at[row_idx, column] = value

        # Save back
        if filepath.endswith('.csv'):
            df.to_csv(filepath, index=False)
        else:
            df.to_excel(filepath, index=False)
        logger.info(f"Updated {filepath}: row {row_idx}, column '{column}' to '{value}'")
        return True
    except Exception as e:
        logger.error(f"Error updating file {filepath}: {e}")
        return False

def encode_url(url):
    """Fully encodes a URL while handling edge cases."""
    # First fix duplicate ? issues
    if url.count('?') > 1:
        parts = url.split('?')
        url = parts[0] + '?' + '&'.join(parts[1:])

    parsed = urlparse(url)

    # Encode path (preserve + for spaces)
    encoded_path = '/'.join(
        quote(segment, safe='+')
        for segment in parsed.path.split('/')
    )

    # Safely parse query (handle multiple = signs)
    query_params = []
    if parsed.query:
        for pair in parsed.query.split('&'):
            if '=' in pair:
                key, *values = pair.split('=')
                query_params.append((key, '='.join(values)))

    # Rebuild URL
    encoded_query = urlencode(query_params) if query_params else ''

    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        encoded_path,
        parsed.params,
        encoded_query,
        parsed.fragment
    ))