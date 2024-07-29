import os
import subprocess
import platform
import camelot
from .utils import remove_unicode_characters
from django.core.files.temp import NamedTemporaryFile
from django.core.files.base import ContentFile

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
    
def convert_doc_to_docx(input_file):
    # 임시 파일 생성
    with NamedTemporaryFile(suffix='.doc') as tmp:
        # 업로드된 파일 내용을 임시 파일에 쓰기
        for chunk in input_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name  # 임시 파일 경로 저장
        print(f"Temporary file created at: {tmp_path}")
    
    # 출력 파일 경로 설정
    output_dir = os.path.dirname(tmp_path)
    output_path = tmp_path.replace('.doc', '.docx')
    print(f"Expected output file path: {output_path}")

    try:
        # LibreOffice를 사용하여 파일 변환
        if platform.system() == 'Windows':
            libreoffice_path = r'C:\Program Files\LibreOffice\program\soffice.exe'  # LibreOffice 실행 파일 경로
        else:
            libreoffice_path = 'libreoffice'  # 리눅스 또는 맥에서는 일반적으로 libreoffice로 실행 가능

        print(f"Using LibreOffice executable at: {libreoffice_path}")
        
        result = subprocess.run([
            libreoffice_path, '--convert-to', 'docx', '--headless',
            '--outdir', output_dir, tmp_path
        ], check=True)
        
        print(f"LibreOffice conversion result: {result}")

        # 변환된 파일 경로 확인
        converted_file = os.path.join(output_dir, os.path.splitext(os.path.basename(tmp_path))[0] + '.docx')
        print(f"Converted file should be at: {converted_file}")

        if os.path.exists(converted_file):
            print(f"Converted file found at: {converted_file}")
            with open(converted_file, 'rb') as f:
                docx_content = f.read()
        else:
            raise FileNotFoundError(f"Converted file not found: {converted_file}")

    finally:
        # 임시 파일 및 변환된 파일 삭제
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
            print(f"Temporary file deleted: {tmp_path}")
        if os.path.exists(converted_file):
            os.unlink(converted_file)
            print(f"Converted file deleted: {converted_file}")

    # ContentFile을 사용하여 Django에서 사용 가능한 파일 객체로 변환
    return ContentFile(docx_content, name=os.path.basename(output_path))

