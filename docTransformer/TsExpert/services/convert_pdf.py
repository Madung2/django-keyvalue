import os
import subprocess
import platform
import camelot
#import pypandoc
from .utils import remove_unicode_characters
#from django.core.files.temp import Named/TemporaryFile
from tempfile import NamedTemporaryFile, mkstemp
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.html import escape

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
    # 임시 파일을 수동으로 생성
    tmp_fd, tmp_path = mkstemp(suffix='.doc')
    os.close(tmp_fd)

    # 업로드된 파일 내용을 임시 파일에 쓰기
    with open(tmp_path, 'wb') as tmp:
        for chunk in input_file.chunks():
            tmp.write(chunk)
    print(f"임시 파일 생성됨: {tmp_path}")
    
    # 출력 파일 경로 설정
    output_path = tmp_path.replace('.doc', '.docx')
    print(f"예상 출력 파일 경로: {output_path}")

    try:
        # LibreOffice를 사용하여 파일 변환
        if platform.system() == 'Windows':
            libreoffice_path = r'C:\Program Files\LibreOffice\program\soffice.exe'  # LibreOffice 실행 파일 경로
        else:
            libreoffice_path = 'libreoffice'  # 리눅스 또는 맥에서는 일반적으로 libreoffice로 실행 가능

        print(f"LibreOffice 실행 파일 경로: {libreoffice_path}")
        
        result = subprocess.run([
            libreoffice_path, '--convert-to', 'docx', '--headless',
            '--outdir', os.path.dirname(tmp_path), tmp_path
        ], capture_output=True, text=True)

        print(f"LibreOffice 변환 결과: {result.stdout}")
        print(f"LibreOffice 변환 오류: {result.stderr}")

        if result.returncode != 0:
            raise Exception(f"LibreOffice 변환 오류: {result.stderr}")

        # 변환된 파일 경로 확인
        converted_file = os.path.join(os.path.dirname(tmp_path), os.path.splitext(os.path.basename(tmp_path))[0] + '.docx')
        print(f"변환된 파일 경로: {converted_file}")

        if os.path.exists(converted_file):
            print(f"변환된 파일 확인됨: {converted_file}")
            with open(converted_file, 'rb') as f:
                docx_content = f.read()
        else:
            raise FileNotFoundError(f"변환된 파일을 찾을 수 없음: {converted_file}")

    finally:
        # 임시 파일 및 변환된 파일 삭제
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
            print(f"임시 파일 삭제됨: {tmp_path}")
        if os.path.exists(converted_file):
            os.unlink(converted_file)
            print(f"변환된 파일 삭제됨: {converted_file}")

    # ContentFile을 사용하여 Django에서 사용 가능한 파일 객체로 변환
    return ContentFile(docx_content, name=os.path.basename(output_path)), converted_file



def convert_hwp_to_docx(input_file):
    # 임시 파일을 수동으로 생성
    tmp_fd, tmp_path = mkstemp(suffix='.hwp')
    os.close(tmp_fd)

    # 업로드된 파일 내용을 임시 파일에 쓰기
    with open(tmp_path, 'wb') as tmp:
        for chunk in input_file.chunks():
            tmp.write(chunk)
    print(f"임시 파일 생성됨: {tmp_path}")
    
    # 출력 파일 경로 설정
    output_dir = os.path.dirname(tmp_path)
    output_path = tmp_path.replace('.hwp', '.docx')
    print(f"예상 출력 파일 경로: {output_path}")

    try:
        # LibreOffice를 사용하여 파일 변환
        if platform.system() == 'Windows':
            libreoffice_path = r'C:\Program Files\LibreOffice\program\soffice.exe'  # LibreOffice 실행 파일 경로
        else:
            libreoffice_path = 'libreoffice'  # 리눅스 또는 맥에서는 일반적으로 libreoffice로 실행 가능

        print(f"LibreOffice 실행 파일 경로: {libreoffice_path}")
        
        result = subprocess.run([
            libreoffice_path, '--convert-to', 'docx', '--headless',
            '--outdir', output_dir, tmp_path
        ], check=True)
        
        print(f"LibreOffice 변환 결과: {result}")

        # 변환된 파일 경로 확인
        converted_file = os.path.join(output_dir, os.path.splitext(os.path.basename(tmp_path))[0] + '.docx')
        print(f"변환된 파일 경로: {converted_file}")

        if os.path.exists(converted_file):
            print(f"변환된 파일 확인됨: {converted_file}")
            with open(converted_file, 'rb') as f:
                docx_content = f.read()
        else:
            raise FileNotFoundError(f"변환된 파일을 찾을 수 없음: {converted_file}")

    finally:
        # 임시 파일 및 변환된 파일 삭제
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
            print(f"임시 파일 삭제됨: {tmp_path}")
        if os.path.exists(converted_file):
            os.unlink(converted_file)
            print(f"변환된 파일 삭제됨: {converted_file}")

    # ContentFile을 사용하여 Django에서 사용 가능한 파일 객체로 변환
    return ContentFile(docx_content, name=os.path.basename(output_path))


# def convert_to_docx(input_file, file_extension):
#     # 임시 파일을 수동으로 생성
#     tmp_fd, tmp_path = mkstemp(suffix=f'.{file_extension}')
#     os.close(tmp_fd)

#     # 업로드된 파일 내용을 임시 파일에 쓰기
#     with open(tmp_path, 'wb') as tmp:
#         for chunk in input_file.chunks():
#             tmp.write(chunk)
#     print(f"임시 파일 생성됨: {tmp_path}")
    
#     # 변환된 파일을 저장할 디렉토리 경로 설정
#     converted_dir = os.path.join(settings.MEDIA_ROOT, 'documents', 'converted')
#     os.makedirs(converted_dir, exist_ok=True)
    
#     # 출력 파일 경로 설정
#     output_path = os.path.join(converted_dir, os.path.basename(tmp_path).replace(f'.{file_extension}', '.docx'))
#     print(f"예상 출력 파일 경로: {output_path}")

#     try:
#         # LibreOffice를 사용하여 파일 변환
#         if platform.system() == 'Windows':
#             libreoffice_path = r'C:\Program Files\LibreOffice\program\soffice.exe'  # LibreOffice 실행 파일 경로
#         else:
#             libreoffice_path = 'libreoffice'  # 리눅스 또는 맥에서는 일반적으로 libreoffice로 실행 가능

#         print(f"LibreOffice 실행 파일 경로: {libreoffice_path}")
        
#         result = subprocess.run([
#             libreoffice_path, '--convert-to', 'docx', '--headless',
#             '--outdir', converted_dir, tmp_path
#         ], capture_output=True, text=True)

#         print(f"LibreOffice 변환 결과: {result.stdout}")
#         print(f"LibreOffice 변환 오류: {result.stderr}")

#         if result.returncode != 0:
#             raise Exception(f"LibreOffice 변환 오류: {result.stderr}")

#         # 변환된 파일 경로 확인
#         converted_file = os.path.join(converted_dir, os.path.splitext(os.path.basename(tmp_path))[0] + '.docx')
#         print(f"변환된 파일 경로: {converted_file}")

#         if os.path.exists(converted_file):
#             print(f"변환된 파일 확인됨: {converted_file}")
#             with open(converted_file, 'rb') as f:
#                 docx_content = f.read()
#         else:
#             raise FileNotFoundError(f"변환된 파일을 찾을 수 없음: {converted_file}")

#     finally:
#         # 임시 파일 삭제
#         if os.path.exists(tmp_path):
#             os.unlink(tmp_path)
#             print(f"임시 파일 삭제됨: {tmp_path}")

#     # ContentFile을 사용하여 Django에서 사용 가능한 파일 객체로 변환
#     return ContentFile(docx_content, name=os.path.basename(output_path)), converted_file

def convert_to_docx(input_file, file_extension):
    # 임시 파일을 수동으로 생성
    tmp_fd, tmp_path = mkstemp(suffix=f'.{file_extension}')
    os.close(tmp_fd)

    # 업로드된 파일 내용을 임시 파일에 쓰기
    with open(tmp_path, 'wb') as tmp:
        for chunk in input_file.chunks():
            tmp.write(chunk)
    print(f"임시 파일 생성됨: {tmp_path}")
    
    # 변환된 파일을 저장할 디렉토리 경로 설정
    converted_dir = os.path.join(settings.MEDIA_ROOT, 'documents', 'converted')
    os.makedirs(converted_dir, exist_ok=True)
    
    # 출력 파일 경로 설정
    output_path = os.path.join(converted_dir, os.path.basename(tmp_path).replace(f'.{file_extension}', '.docx'))
    print(f"예상 출력 파일 경로: {output_path}")

    try:
        # LibreOffice를 사용하여 파일 변환
        if platform.system() == 'Windows':
            libreoffice_path = r'C:\Program Files\LibreOffice\program\soffice.exe'  # LibreOffice 실행 파일 경로
        else:
            libreoffice_path = 'libreoffice'  # 리눅스 또는 맥에서는 일반적으로 libreoffice로 실행 가능

        print(f"LibreOffice 실행 파일 경로: {libreoffice_path}")
        
        result = subprocess.run([
            libreoffice_path, '--convert-to', 'docx', '--headless',
            '--outdir', converted_dir, tmp_path
        ], capture_output=True, text=True)

        print(f"LibreOffice 변환 결과: {result.stdout}")
        print(f"LibreOffice 변환 오류: {result.stderr}")

        if result.returncode != 0:
            raise Exception(f"LibreOffice 변환 오류: {result.stderr}")

        # 변환된 파일 경로 확인
        converted_file = os.path.join(converted_dir, os.path.splitext(os.path.basename(tmp_path))[0] + '.docx')
        print(f"변환된 파일 경로: {converted_file}")

        if os.path.exists(converted_file):
            print(f"변환된 파일 확인됨: {converted_file}")
            with open(converted_file, 'rb') as f:
                docx_content = f.read()
        else:
            raise FileNotFoundError(f"변환된 파일을 찾을 수 없음: {converted_file}")

    finally:
        # 임시 파일 삭제
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
            print(f"임시 파일 삭제됨: {tmp_path}")

    # 변환된 파일 URL 생성
    converted_file_url = os.path.join(settings.MEDIA_URL, 'documents', 'converted', os.path.basename(converted_file))
    # converted_file_url = escape(converted_file_url)  # URL을 안전하게 인코딩
    converted_file_url = converted_file_url.replace('\\', '/')  # URL을 올바른 형식으로 변환

    # ContentFile을 사용하여 Django에서 사용 가능한 파일 객체로 변환
    return ContentFile(docx_content, name=os.path.basename(output_path)), converted_file_url