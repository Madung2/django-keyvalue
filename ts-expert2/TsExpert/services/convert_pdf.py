import os
import subprocess
import camelot
from .utils import remove_unicode_characters


def convert_docx_to_pdf(input_path, output_path):
    """
    Connect to a remote LibreOffice service using unoconv to convert a DOCX file to a PDF file.

    :param input_path: Path to the input DOCX file.
    :param output_path: Path to the output PDF file.
    """
    print(1111, input_path, output_path)
    # Run the unoconv command to convert the file
    print('this222')
    try:
        # Assuming unoconv server is running on localhost:2003
        result = subprocess.run(['docker', 'exec',  '-u', 'worker',  'unoserver', 'unoconvert', '/home/worker/data/sample.docx',  'sample.pdf'])
        print(f'Successfully converted {input_path} to {output_path}')
        # Print the output
        print("Output:", result.stdout)
        print("Error:", result.stderr)
        print("Return Code:", result.returncode)
        result = subprocess.run(['docker', 'cp', 'unoserver:/home/worker/sample.pdf',  '/data/sample.pdf'])
        print(f'Successfully converted {input_path} to {output_path}')
        # Print the output
        print("Output:", result.stdout)
        print("Error:", result.stderr)
        print("Return Code:", result.returncode)

        # Read tables from the converted PDF using Camelot
        tables = camelot.read_pdf(output_path, pages='1-5')
        print(len(tables))
        return tables
    except Exception as e:
        print(f"An error occurred: {e}")
        return None