# ds-sanitize-NumberVarianceReducer
Command-line tool that reduces the precision of numerical data (e.g., rounding to nearest integer or specified decimal place) to minimize re-identification risks from statistical analysis. Accepts a CSV or JSON file and a column name as input. Uses the pandas library. - Focused on Tools for anonymizing and redacting sensitive data within datasets and files. Supports techniques like data masking, pseudonymization, and generalization to protect privacy while retaining data utility for testing and development. Leverages libraries for data generation and dataframe manipulation.

## Install
`git clone https://github.com/ShadowStrikeHQ/ds-sanitize-numbervariancereducer`

## Usage
`./ds-sanitize-numbervariancereducer [params]`

## Parameters
- `-h`: Show help message and exit
- `--precision`: No description provided
- `--output_file`: No description provided
- `--file_type`: Specify the file type: csv or json. If not specified, it will be inferred from the file extension.

## License
Copyright (c) ShadowStrikeHQ
