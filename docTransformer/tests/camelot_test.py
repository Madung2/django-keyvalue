import camelot

import camelot

# Specify the PDF file you want to extract tables from
#pdf_file = "path/to/your/file.pdf"  # Replace with the actual path to your PDF file

# Extract tables from all pages
file_path = 'docx_pdf.pdf'
tables = camelot.read_pdf(file_path, pages='all',flavor='stream')

# Check the number of tables found
print(f"Number of tables found: {len(tables)}")

# Iterate through each table and display its content
for i, table in enumerate(tables):
    print(f"\nTable {i + 1} DataFrame:")
    print(table.df)  # Print the extracted table as a DataFrame

    # Optionally, save the table to a CSV file
    output_file = f'table_{i + 1}.csv'
    table.to_csv(output_file)
    print(f"Table {i + 1} saved to {output_file}")
