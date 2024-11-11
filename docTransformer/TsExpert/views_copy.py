import io
import pandas as pd
from docx import Document
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from .services.extract import KeyValueExtractor
from .services.nested_table import NestedTableExtractor
from .services.image_and_table_ext import extract_images_from_tables, extract_table_from_raw_paragraphs
from .services.post_process import post_process
#from .services.convert_pdf import convert_doc_to_docx, convert_hwp_to_docx
from .services.convert_pdf import convert_to_docx
# from .services.DocGenerator import DocxHTMLParser, DocxGenerator
from .models import Task, ExtractDictionary, IMExtraction
from pdf2docx import Converter
from django.http import HttpResponse
# from .tasks import save_data_task
import os
import tempfile
import PyPDF2
import json
import magic
import camelot
#import pdfplumber
##################################################
from django.shortcuts import render


NAS_BASE_PATH = settings.NAS_BASE_PATH
print('NAS_BASE_PATH:', NAS_BASE_PATH)

def render_tsexpert(req):
    return render(req, 'TsExpert.html')


def render_docGenerator(req):
    return render(req, 'docGenerator.html')

def convert_pdf_to_docx(pdf_file):
    docx_file_path = 'temp_output.docx'
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
        temp_pdf.write(pdf_file.read())
        temp_pdf_path = temp_pdf.name

    cv = Converter(temp_pdf_path)
    cv.convert(docx_file_path)
    cv.close()

    os.remove(temp_pdf_path)
    return docx_file_path

def get_mime_type(content):
    """Determines the MIME type of a given file."""
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(content)  # Read first 1024 bytes to determine MIME type
    input_file.seek(0)  # Reset the file pointer to the beginning
    print('MIME type:', mime_type)
    return mime_type

def check_file_type(content, target_mime_types):
    """Checks if the file's MIME type matches one of the target MIME types."""
    mime_type = get_mime_type(content)
    return mime_type in target_mime_types

def is_pdf_file(input_file):
    """Checks if the input file is a PDF."""
    return check_file_type(input_file, {'application/pdf'})

def is_doc_file(input_file):
    """Checks if the input file is a DOC or DOCX file."""
    return check_file_type(input_file, {
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    })

def is_hwp_file(input_file):
    """Checks if the input file is a HWP file."""
    return check_file_type(input_file, {'application/x-hwp'})

def extract_first_5_pages(input_pdf_path, output_pdf_path):
    # PDF 파일 읽기
    with open(input_pdf_path, 'rb') as input_pdf_file:
        pdf_reader = PyPDF2.PdfReader(input_pdf_file)
        pdf_writer = PyPDF2.PdfWriter()

        # 첫 5페이지 추출
        num_pages = min(len(pdf_reader.pages), 5)
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

        # 새로운 PDF 파일로 저장
        with open(output_pdf_path, 'wb') as output_pdf_file:
            pdf_writer.write(output_pdf_file)
        # print(f"Extracted first {num_pages} pages to {output_pdf_path}")

##################################################
default_key_value = [
    {"key": "투자형태", "type": "string", "is_table": False, "synonym": {"priority": [], "all": [], "pattern": []}, "specific": False, "sp_word": None, "value": ["블라인드펀드", "기업투자"], "split": []}, 
    {"key": "신청부팀점", "type": "department", "is_table": True, "synonym": {"priority": ["신청부서"], "all": ["신청부서"], "pattern": ["투자금융\\d+부"]}, "specific": False, "sp_word": None, "value": [], "split": []},
    {"key": "신청직원", "type": "name", "is_table": False, "synonym": {"priority": ["담당", "작성자", "매니저"], "all": ["담당", "작성자", "매니저"], "pattern": []}, "specific": False, "sp_word": None, "value": [], "split": []}, 
    {"key": "신청일자", "type": "date", "is_table": False, "synonym": {"priority": ["신청일자"], "all": ["신청일자"], "pattern": []}, "specific": False, "sp_word": None, "value": [], "split": []}, 
    {"key": "고객명", "type": "string", "is_table": True, "synonym": {"priority": ["펀드명"], "all": ["펀드명"], "pattern": []}, "specific": False, "sp_word": None, "split": []}, 
    {"key": "상품", "type": "string", "is_table": True, "synonym": {"priority": ["계정명"], "all": ["계정명"], "pattern": []}, "specific": False, "sp_word": None, "split": []}, 
    {"key": "펀드형태", "type": "string", "is_table": True, "synonym": {"priority": ["펀드유형", "펀드형태"], "all": ["펀드유형", "펀드형태", "펀드성격", "투자 기구"], "pattern": []}, "specific": False, "sp_word": None, "split": []}, 
    {"key": "출자자명", "type": "string", "is_table": True, "synonym": {"priority": ["GP", "집합투자업자"], "all": ["GP", "집합투자업자"], "pattern": []}, "specific": False, "sp_word": None, "split": []}, 
    {"key": "존속기간", "type": "year", "is_table": True, "synonym": {"priority": ["존속기간", "펀드기간", "펀드존속기간"], "all": ["존속기간", "펀드기간", "펀드존속기간", "펀드만기"], "pattern": []}, "specific": False, "sp_word": None, "split": []}, 
    {"key": "출자약정금액", "type": "money", "is_table": True, "synonym": {"priority": ["GP 출자금", "최소결성금액", "펀드규모"], "all": ["펀드약정총액", "GP출자금", "현재 약정금액", "펀드규모", "목표모집금액", "최소결성금액", "결성금액"], "pattern": []}, "specific": False, "sp_word": None, "split": []}, 
    {"key": "약정금액", "type": "money", "is_tab le": True, "synonym": {"priority": ["LP", "당사 출자금액"], "all": ["LP", "당사 출자금액", "당사참여규모", "당사 신청금액", "당사 출자 요청액"], "pattern": []}, "specific": True, "sp_word": "당사", "split": []}, 
    {"key": "승인신청금액", "type": "money", "is_table": True, "synonym": {"priority": ["신청금액"], "all": ["신청금액"], "pattern": []}, "specific": False, "sp_word": None, "split": []}, 
    {"key": "출자가능기간", "type": "year", "is_table": True, "synonym": {"priority": ["투자기간", "펀드투자기간"], "all": ["투자기간", "펀드투자기간"], "pattern": []}, "specific": False, "sp_word": None, "split": []}, 
    {"key": "기준수익률", "type": "percentage", "is_table": True, "synonym": {"priority": ["기준수익률"], "all": ["기준수익률", "성과보수율", "성과보수", "성공보수"], "pattern": []}, "specific": False, "sp_word": ["IRR", "기준수익률"], "split": ["초과", "상회"]}, 
    {"key": "성과보수율", "type": "percentage", "is_table": True, "synonym": {"priority": ["성과보수"], "all": ["성과보수율", "성과보수", "성공보수"], "pattern": []}, "specific": False, "sp_word": ["초과", "상회"], "split": ["초과", "상회"]}, 
    {"key": "목표수익률", "type": "percentage", "is_table": True, "synonym": {"priority": ["목표수익률"], "all": ["예상수익률", "목표수익률"], "pattern": []}, "specific": False, "sp_word": ["기준"], "split": ["기준"]}
    ]
IM_key_value = [
    {"key": "차주사", "val_type": "string", "val_syn": ["차주사", "차주(시행사)", "차주"], "val_ext_method": [], "val_ext_form":"str_no_braket"},
    {"key": "신탁사", "val_type": "string", "val_syn": ["신탁사"], "val_ext_method": [], "val_ext_form":"str_no_braket"},
    {"key": "금융주관사", "val_type": "string", "val_syn": ["대리금융기관"], "val_ext_method": [], "val_ext_form":"str_no_braket"},
    {"key": "금융구조도", "val_type": "image", "val_syn": ["금융구조도", "구조도"], "val_ext_method": [], "val_ext_form":"str_no_braket"},
    {"key": "대출금액", "val_type": "string", "val_syn": ["대출금액"], "val_ext_method": [], "val_ext_form":"str_no_braket"},
    {"key": "대출기간", "val_type": "string", "val_syn": ["대출만기"], "val_ext_method": [], "val_ext_form":"str_no_braket"},
    {"key": "이자지급방식", "val_type": "string", "val_syn": ["이자지급"], "val_ext_method": [], "val_ext_form":"str_no_braket"},
    {"key": "인출방법", "val_type": "string", "val_syn": ["인출방식"], "val_ext_method": [], "val_ext_form":"str_no_braket"},
    {"key": "연체가산금리", "val_type": "string", "val_syn": ["연체이자율"], "val_ext_method": [], "val_ext_form":"str_no_braket"},
    {"key": "상환방법", "val_type": "string", "val_syn": ["상환방법"], "val_ext_method": [], "val_ext_form":"str_no_braket"},
    {"key": "조기상환수수료", "val_type": "string", "val_syn": ["조기상환수수료", "조기상환"], "val_ext_method": [], "val_ext_form":"percentage"},
    {"key": "대출금리", "val_type": "string", "val_syn": ["대출금리"], "val_ext_method": [], "val_ext_form":"percentage"},
    {"key": "채권보전", "val_type": "string", "val_syn": ["채권보전"], "val_ext_method": [], "val_ext_form":"str_no_braket"},
    {"key": "인출선행조건", "val_type": "string", "val_syn": ["인출선행조건"], "val_ext_method": [], "val_ext_form":""},
    {"key": "인출후행조건", "val_type": "string", "val_syn": ["인출후행조건"], "val_ext_method": [], "val_ext_form":""},
    {"key": "분양수입금 납입비율", "val_type": "string", "val_syn": ["납입비율"], "val_ext_method": [], "val_ext_form":""},
    {"key": "분양수입금 비율", "val_type": "string", "val_syn": ["납입비율"], "val_ext_method": [], "val_ext_form":""},
]
appraisal_key_value = [

]



def get_meta_data(file_type):
    """ExtractDictionary 모델에서 doc_type_id로 필터하고, 그중 가장 최신것을 가져온다.

    Returns:
        _type_: _description_
    """
    print('2:get_meta_data')
   #dictionary_data = ExtractDictionary.objects.filter(document_type= file_type).order_by('-edited_at').first() ## 내가 원하는 document_type 으로 filter하고 orider_by('-id')
    #return dictionary_data.dictionary

    ## 일단 외부에서는 이렇게 간다.
    if file_type == 100: # IM 문서
        return IM_key_value
    elif file_type == 200: #감정평가서 문서
        return appraisal_key_value



def run_data_extract2(file, file_type, key_value):
    print('1:run_data_extract')

    doc = Document(file)
    ext = KeyValueExtractor(doc, key_value)
    text_data, image_data = ext.extract_data()

    nest = NestedTableExtractor(doc, key_value)
    nest_data = nest.extract_all_data()


    final_data = post_process(text_data, key_value)
    #### type1)
    for k, v in nest_data.items():
        v_as_str = json.dumps(v, ensure_ascii=False)  # v를 JSON 문자열로 변환
        new_d = [k, v, k , 0]
        final_data.append(new_d)

    image_info = extract_images_from_tables(doc, image_data)

    xml_info =extract_table_from_raw_paragraphs(file, key_value)#'사업개요')


    return final_data, image_info,xml_info

def run_data_extract3(file_path, file_type, key_value_list):
    """_summary_

    Args:
        file_path (_type_): string 위치
        file_type (_type_): file_type 이거 필요없을 수도 있음
        key_value (_type_): 실제 딕셔너리

    Returns:
        text_data:  [[key, value, page, pos]] 
        image_data: [[key, value, page, pos]]
        table_data: [[key, value, page, pos]]
    """
    text_data = [["key", "value", "page", 'pos']]
    image_data = [["key", "value", "page", 'pos']]
    table_data = [["key", "value", "page", 'pos']]
    string_key_value = [kv for kv in IM_key_value if kv['val_type'] == 'string']
    table_key_value = [kv for kv in IM_key_value if kv['val_type'] == 'table']
    image_key_value = [kv for kv in IM_key_value if kv['val_type'] == 'image']
    print('string_key_value', string_key_value, flush=True)
    
    tables = camelot.read_pdf(file_path, pages='all')

    with pdfplumber.open(file_path) as pdf:
        # Text data extraction
        for i, table in enumerate(tables):
            page_number = table.parsing_report['page']
            print(table.df)
            for index, row in table.df.iterrows():  # Iterate through each row
                for key_dict in string_key_value:
                    key = key_dict["key"]
                    synonyms = key_dict.get("val_syn", [])
                    print('key', key, flush=True)
                    print('syn', synonyms, flush=True)
                    
                    # Check if any synonym is in row values
                    if any(synonym in row.values for synonym in synonyms):
                        print(f"Found match for key '{key}' using synonyms: {synonyms}", flush=True)
                        
                        # Extract remaining value(s) from the row
                        filtered_values = [value for value in row.values if value not in synonyms]
                        extracted_value = next((ele for ele in filtered_values if ele != ''), '')
                        
                        # Get position information using pdfplumber
                        page = pdf.pages[page_number - 1]  # pdfplumber uses zero-based index
                        words = page.extract_words()
                        pos = None
                        for word in words:
                            if extracted_value in word['text']:
                                pos = (word['x0'], word['top'], word['x1'], word['bottom'])  # Bounding box coordinates
                                break
                        
                        # Append extracted data to text_data
                        text_data.append([key, extracted_value, page_number, pos if pos else 'pos not found'])
        # Image and Table data extraction
        for i, page in enumerate(pdf.pages):
            page_number = i + 1
            # Process image data
            for key_dict in image_key_value:
                key = key_dict["key"]
                synonyms = key_dict.get("val_syn", [])
                words = page.extract_words()
                
                # Find the first occurrence of any synonym
                pos = None
                for word in words:
                    if any(synonym in word['text'] for synonym in synonyms):
                        pos = (word['x0'], word['top'], word['x1'], word['bottom'])  # Bounding box coordinates
                        break
                
                if pos:
                    # Find the first image below the found text
                    images = page.images
                    image_below = None
                    for image in images:
                        if image["top"] > pos[1]:  # Ensure it's below the found text
                            image_below = image
                            break
                    
                    if image_below:
                        image_value = f"Image at {image_below['x0']},{image_below['top']}"  # Customize this value as needed
                        image_pos = (image_below['x0'], image_below['top'], image_below['x1'], image_below['bottom'])
                        image_data.append([key, image_value, page_number, image_pos])
            
            # Process table data
            for key_dict in table_key_value:
                key = key_dict["key"]
                synonyms = key_dict.get("val_syn", [])
                words = page.extract_words()
                
                # Find the first occurrence of any synonym
                pos = None
                for word in words:
                    if any(synonym in word['text'] for synonym in synonyms):
                        pos = (word['x0'], word['top'], word['x1'], word['bottom'])  # Bounding box coordinates
                        break
                
                if pos:
                    # Assuming you want to add tables near this position, this part needs clarification on what you mean by table extraction
                    # For now, placeholder behavior is shown
                    table_data.append([key, "Table data placeholder", page_number, pos])

    return text_data, image_data, table_data

def save_in_db(data, image_data, xml_data, key_value):
    """data 는 [[k,v,k pos], ...]

    Args:
        data (list of lists): [[k,v,k pos], ...]
        key_value (_type_): _description_
    """
    # IMExtraction 인스턴스를 생성합니다. 필요한 경우 여기에 특정 인스턴스를 로드하거나 수정할 수도 있습니다.
    im_extraction_instance = IMExtraction()

    # IMExtraction 모델의 필드들을 가져옵니다.
    fields = IMExtraction._meta.get_fields()

    # data를 순회하면서 k 값을 verbose_name과 비교
    for d in data:#
        k = d[0]  # verbose_name에 해당하는 값
        v = d[1]  # 저장할 값

        # 모델 필드를 순회하면서 k와 매칭되는 필드를 찾음
        for field in fields:
            # 필드에 verbose_name이 있는지 확인
            if hasattr(field, 'verbose_name') and field.verbose_name == k:
                # 매칭되는 필드에 값을 할당
                setattr(im_extraction_instance, field.name, v)
                break  # 매칭되면 더 이상 필드를 찾을 필요 없음

    # Save image data
    for img_key, img in image_data:
        for field in fields:
            if hasattr(field, 'verbose_name') and field.verbose_name == img_key:
                # Assuming the field is an ImageField
                field_name = field.name
                setattr(im_extraction_instance, field_name, img)  # Set the image
                break

    for xml_key, xml in xml_data:
        for field in fields:
            if hasattr(field, 'verbose_name') and field.verbose_name == xml_key:
                setattr(im_extraction_instance, field.name, xml)
                break

    # 인스턴스 저장
    im_extraction_instance.save()




from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import io




def process_file(file_type, file):
    """Helper function to handle file processing and conversion based on file input.
    file_type = 100 (int) IM 문서, 200(감정평가서), 영업의견서
    file = InMemoryUploadedFile or file path string (depending on context)
    """
    print('file_type', type(file_type), file_type)
    print('file', type(file), file)
    # try:
        # Determine if the input is a file object (InMemoryUploadedFile) or a file path string
    if hasattr(file, 'read'):  # Check if `file` is an uploaded file object
        content = file.read()  # Read file content if it's an uploaded file
        file_path = f"/tmp/{file.name}"  # Temporary file path (adjust as needed)
        
        # Save the uploaded file to a temporary location if needed
        with open(file_path, 'wb') as temp_file:
            temp_file.write(content)
    else:
        # Assume `file` is a file path
        file_path = os.path.join(NAS_BASE_PATH, file)  # Join base path if needed
        # Check if the file exists
        if not os.path.exists(file_path):
            return None, {"error": f"File not found at path: {file}"}, status.HTTP_404_NOT_FOUND
        
        # Open the file and read content
        with open(file_path, 'rb') as file_obj:
            content = file_obj.read()

    # File processing logic
    print(1)
    file_url = None
    # Example branching based on file type, can be customized
    # if is_doc_file(content) or is_hwp_file(content):
    #     file, file_url = convert_to_docx(file, file_type)
    # elif is_pdf_file(content):
    #     file, file_url = convert_pdf_to_docx(file)
    print(2)
    # Data extraction
    key_value = get_meta_data(file_type)
    result, image_data, xml_data = run_data_extract3(file_path, file_type, key_value)
    print(3)
    # Optionally save results in a database
    # save_in_db(result, image_data, xml_data, key_value)
    return result, {"file_url": file_url}, None

    # except Exception as e:
    #     # Handle exceptions gracefully
    #     return None, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR


@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser])
def extract_key_value(request):
    """API endpoint for extracting key-value pairs from a file."""

    result, file_url_response, error = process_file(request)
    if error:
        return Response(file_url_response, status=error)

    # response_data = {
    #     "data": result,
    #     "file_url": file_url_response.get('file_url')
    # }
    # return JsonResponse(response_data, safe=False)
    response_data = []
    for k, v, ele3, ele4 in result:
        response_data.append({"group":k, "final_output":v})
    return JsonResponse(response_data, safe=False)

@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser])
def extract_term_sheet(request):
    """API endpoint for extracting term sheet data."""
    result, file_url_response, error = process_file(request)
    print(result)
    if error:
        return Response(file_url_response, status=error)
    
    # #### HANA ###
    response_data = {}
    for title, ele1, ele2, ele3 in result:
        if type(title)==str and type(ele1) == str:
            response_data[title] = ele1
    return JsonResponse([response_data], safe=False)

    #### NICE ####
    response_data = []
    for key, value, ele2, ele3 in result:
        ele = {"group": key, "serial_number": 0, "mandatory_field": "", "final_output": value}
        response_data.append(ele)
    return JsonResponse(response_data, safe=False)
    


@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def extract(request):
    """API endpoint for extracting key-value pairs from uploaded files."""

    # Collecting files from the request
    file_1 = request.FILES.get('file_1')
    file_2 = request.FILES.get('file_2')
    file_type_1 = request.data.get('file_type_1')
    file_name_1 = request.data.get('file_name_1')
    file_type_2 = request.data.get('file_type_2')
    file_name_2 = request.data.get('file_name_2')

    response_data = []
    errors = []
    print(request.data, flush=True)
    # Process file_1 if present
    if file_1 and file_type_1:
        # Example of using file_1.name
        print(f"Processing file: {file_1.name}")  # file_1.name is a string
        result_1, file_url_response_1, error_1 = process_file(file_type_1, file_1)
        if error_1:
            errors.append({"error": file_url_response_1, "input": {"file_name": file_name_1, "file_type": file_type_1}})
        else:
            response_data.append({
                'file_name': file_name_1,
                'file_type': file_type_1,
                'data': result_1 #format_result(result_1)  # Assuming you have a function to format results
            })
    elif file_1 or file_type_1:
        errors.append({"error": "Missing file_1 or file_type_1 in the request."})

    # Process file_2 if present
    if file_2 and file_type_2:
        # Example of using file_2.name
        print(f"Processing file: {file_2.name}")  # file_2.name is a string
        result_2, file_url_response_2, error_2 = process_file(file_type_2, file_2)
        if error_2:
            errors.append({"error": file_url_response_2, "input": {"file_name": file_name_2, "file_type": file_type_2}})
        else:
            response_data.append({
                'file_name': file_name_2,
                'file_type': file_type_2,
                'data': format_result(result_2)  # Assuming you have a function to format results
            })
    elif file_2 or file_type_2:
        errors.append({"error": "Missing file_2 or file_type_2 in the request."})

    # Prepare the response
    response = {"res": response_data, 'job_id': 1}  # Adjust job_id logic as needed
    if errors:
        response["errors"] = errors
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    return Response(response, status=status.HTTP_200_OK)