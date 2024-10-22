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
##################################################

from django.shortcuts import render

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

def is_pdf_file(input_file):
    print('input_file_name:', input_file.name)
    return input_file.name.split('.')[-1]=='pdf'
def is_doc_file(input_file):
    print('input_file_name:', input_file.name)
    return input_file.name.split('.')[-1]=='doc'

def is_hwp_file(input_file):
    print('input_file_name:', input_file.name)
    return input_file.name.split('.')[-1]=='hwp'


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


def get_meta_data(doc_type_id):
    """ExtractDictionary 모델에서 doc_type_id로 필터하고, 그중 가장 최신것을 가져온다.

    Returns:
        _type_: _description_
    """
    print('2:get_meta_data')
    dictionary_data = ExtractDictionary.objects.filter(document_type= doc_type_id).order_by('-edited_at').first() ## 내가 원하는 document_type 으로 filter하고 orider_by('-id')
    return dictionary_data.dictionary



def run_data_extract2(file, doc_type_id, key_value):
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


    # print('final_Dtaa:', final_data)
    # print('table_xml:', xml_info[0])
    return final_data, image_info,xml_info

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
    for d in data:
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
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
import io



#✮✮✮✮✮✮✮✮✮✮✮✮✮✮✮✮✮✮✮✮✮✮✮✮✮#
def process_file(request):
    """Helper function to handle file processing and conversion."""
    if 'doc' not in request.FILES:
        return None, {"error": "No file provided"}, status.HTTP_400_BAD_REQUEST
    
    file = request.FILES['doc']
    doc_type_id = request.data.get('doc_type_id', 1)

    file_url = None
    if is_doc_file(file) or is_hwp_file(file):
        file, file_url = convert_to_docx(file, 'doc')
    elif is_pdf_file(file):
        file, file_url = convert_pdf_to_docx(file)
    else:
        pass

    content = file.read()
    key_value = get_meta_data(doc_type_id)
    result, image_data, xml_data = run_data_extract2(io.BytesIO(content), doc_type_id, key_value)
    save_in_db(result, image_data, xml_data,  key_value)
    
    return result, {"file_url": file_url}, None




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
    