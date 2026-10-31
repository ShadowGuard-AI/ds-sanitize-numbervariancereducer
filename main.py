import argparse
import pandas as pd
import json
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description='Reduces the precision of numerical data in a CSV or JSON file.')
    parser.add_argument('input_file', type=str, help='The input CSV or JSON file.')
    parser.add_argument('column_name', type=str, help='The name of the column to sanitize.')
    parser.add_argument('--precision', type=int, default=0, help='The number of decimal places to round to. Defaults to 0 (nearest integer).')
    parser.add_argument('--output_file', type=str, help='The output file (CSV or JSON). It must not be the input file. If not specified, --in-place is required to overwrite the input file.', required=False)
    parser.add_argument('--in-place', action='store_true', help='Overwrite the input file in place. Only used when --output_file is not given.')
    parser.add_argument('--file_type', type=str, choices=['csv', 'json'], help='Specify the file type: csv or json. If not specified, it will be inferred from the file extension.')
    return parser

def sanitize_number_variance(df, column_name, precision):
    """
    Reduces the precision of the specified numerical column in the DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame.
        column_name (str): The name of the column to sanitize.
        precision (int): The number of decimal places to round to.

    Returns:
        pd.DataFrame: The sanitized DataFrame.

    Raises:
        TypeError: If the specified column is not numeric.
        KeyError: if the column does not exist
    """
    try:
        if not pd.api.types.is_numeric_dtype(df[column_name]):
            raise TypeError(f"Column '{column_name}' is not numeric. Please select a numeric column.")

        # pandas rounds half to even, following numpy: a value exactly
        # halfway between two rounded results goes to the even neighbour
        # (2.5 rounds to 2 at precision 0), not away from zero as many
        # readers expect. That is the right default for reducing
        # variance without a systematic upward bias, but it is worth
        # knowing before comparing against a spreadsheet.
        df[column_name] = df[column_name].round(precision)
        return df
    except KeyError as e:
        logging.error(f"Column '{column_name}' not found in the dataframe. Please verify that the column name is correct.")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise

def main():
    """
    Main function to parse arguments, read data, sanitize, and write output.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    input_file = args.input_file
    column_name = args.column_name
    precision = args.precision
    if args.output_file:
        if Path(args.output_file).resolve() == Path(input_file).resolve():
            logging.error("Output file must not be the input file. Choose a different output file, or run with --in-place and no --output_file to overwrite the input.")
            sys.exit(1)
        output_file = args.output_file
    elif args.in_place:
        output_file = input_file
    else:
        logging.error("No output file was given and --in-place was not set. Choose one: pass --output_file for a separate output file, or pass --in-place to overwrite the input file.")
        sys.exit(1)
    file_type = args.file_type

    try:
        # Infer file type if not provided
        if not file_type:
            if input_file.lower().endswith('.csv'):
                file_type = 'csv'
            elif input_file.lower().endswith('.json'):
                file_type = 'json'
            else:
                raise ValueError("Could not infer file type from extension.  Please specify using --file_type.")
            logging.info(f"File type inferred: {file_type}")

        # Read the data
        if file_type == 'csv':
            df = pd.read_csv(input_file)
        elif file_type == 'json':
            df = pd.read_json(input_file)
        else:
            raise ValueError("Invalid file type. Choose 'csv' or 'json'.")


        # Sanitize the data
        df = sanitize_number_variance(df, column_name, precision)

        # Write the output
        if file_type == 'csv':
            df.to_csv(output_file, index=False)
        elif file_type == 'json':
            df.to_json(output_file, orient='records', indent=4)

        logging.info(f"Data sanitization complete. Output written to {output_file}")

    except FileNotFoundError:
        logging.error(f"Input file not found: {input_file}")
        sys.exit(1)
    except ValueError as e:
        logging.error(f"Value Error: {e}")
        sys.exit(1)
    except TypeError as e:
        logging.error(f"Type Error: {e}")
        sys.exit(1)
    except KeyError as e:
        # The sanitize_number_variance function now already logs this error, so we just exit.
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Usage Examples:
# 1. Round values in 'transaction_amount' column of 'data.csv' to the nearest integer and overwrite the file:
#    python main.py data.csv transaction_amount --in-place
#
# 2. Round values in 'latitude' column of 'data.json' to 2 decimal places and save to 'sanitized_data.json':
#    python main.py data.json latitude --precision 2 --output_file sanitized_data.json
#
# 3. Round values in 'price' column of 'data.csv' to 1 decimal place and save to 'output.csv'
#    python main.py data.csv price --precision 1 --output_file output.csv
#
# 4. Explicitly specify the file type when it cannot be inferred from the extension (e.g., if the input file is 'data'):
#    python main.py data sales --file_type csv