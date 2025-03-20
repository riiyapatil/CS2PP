import csv

def process_csv(file_path):
    """
    Process a CSV file and write modified version to current directory.
    
    Args:
        file_path (str): Path to the original CSV file
    
    Returns:
        tuple: (input_path, output_path) file names
    
    Raises:
        FileNotFoundError: If input CSV is missing
    """
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            rows = [row for row in reader]

    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    # Process data - example: keep header + first 100 rows
    processed_rows = rows[:11914]  # Replace with your actual processing

    # Write to fixed output name in current directory
    output_path = "cardata_modified.csv"
    with open(output_path, 'w', newline='', encoding='utf-8') as out_file:
        writer = csv.writer(out_file)
        writer.writerows(processed_rows)

    return (file_path, output_path)
