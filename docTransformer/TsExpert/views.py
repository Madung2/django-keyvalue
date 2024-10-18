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
from .services.extract import KeyValueExtractor, NestedTableExtractor
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
    {"key": "약정금액", "type": "money", "is_table": True, "synonym": {"priority": ["LP", "당사 출자금액"], "all": ["LP", "당사 출자금액", "당사참여규모", "당사 신청금액", "당사 출자 요청액"], "pattern": []}, "specific": True, "sp_word": "당사", "split": []}, 
    {"key": "승인신청금액", "type": "money", "is_table": True, "synonym": {"priority": ["신청금액"], "all": ["신청금액"], "pattern": []}, "specific": False, "sp_word": None, "split": []}, 
    {"key": "출자가능기간", "type": "year", "is_table": True, "synonym": {"priority": ["투자기간", "펀드투자기간"], "all": ["투자기간", "펀드투자기간"], "pattern": []}, "specific": False, "sp_word": None, "split": []}, 
    {"key": "기준수익률", "type": "percentage", "is_table": True, "synonym": {"priority": ["기준수익률"], "all": ["기준수익률", "성과보수율", "성과보수", "성공보수"], "pattern": []}, "specific": False, "sp_word": ["IRR", "기준수익률"], "split": ["초과", "상회"]}, 
    {"key": "성과보수율", "type": "percentage", "is_table": True, "synonym": {"priority": ["성과보수"], "all": ["성과보수율", "성과보수", "성공보수"], "pattern": []}, "specific": False, "sp_word": ["초과", "상회"], "split": ["초과", "상회"]}, 
    {"key": "목표수익률", "type": "percentage", "is_table": True, "synonym": {"priority": ["목표수익률"], "all": ["예상수익률", "목표수익률"], "pattern": []}, "specific": False, "sp_word": ["기준"], "split": ["기준"]}
    ]


def get_key_value_data():
    print('2:get_key_value_data')
    latest_key_value = KeyValue.objects.order_by('-created_at').first()
    # print('lated_key_value:', latest_key_value.key_values)
    return latest_key_value.key_values

# def get_meta_data():
#     print('2:get_meta_data')
#     meta_data_objects = Dictionary.objects.filter(in_use=True)
#     data = []
    
#     for obj in meta_data_objects:
#         item = {
#             "key": obj.key,
#             "type": obj.type,
#             "is_table": obj.is_table,
#             "extract_all_json": obj.extract_all_json,
#             "synonym": {
#                 "priority": json.loads(obj.synonym_all),
#                 "all": json.loads(obj.synonym_all),
#                 "pattern": json.loads(obj.synonym_pattern)
#             },
#             "second_key": json.loads(obj.second_key),
#             "specific": bool(obj.sp_word),
#             "sp_word": obj.sp_word,
#             "value": json.loads(obj.value),
#             "split": json.loads(obj.split),
#             "map": json.loads(obj.map),
#         }
#         data.append(item)
#     print('latest metadata:', data)
#     return data


def get_meta_data(doc_type_id):
    """ExtractDictionary 모델에서 doc_type_id로 필터하고, 그중 가장 최신것을 가져온다.

    Returns:
        _type_: _description_
    """
    print('2:get_meta_data')
    dictionary_data = ExtractDictionary.objects.filter(document_type= doc_type_id).order_by('-edited_at').first() ## 내가 원하는 document_type 으로 filter하고 orider_by('-id')
    print('dictionary_data:', dictionary_data.dictionary)
    return dictionary_data.dictionary


# def run_data_extract(file):
#     print('1:run_data_extract')
#     key_value = get_meta_data()
#     # if settings.METATYPE ==2:
#     #     key_value = get_meta_data()
#     # else:
#     #     key_value = get_key_value_data()
#     # print(dir(file))
#     doc = Document(file)
#     ext = KeyValueExtractor(doc, key_value)
#     data = ext.extract_data()

#     nest = NestedTableExtractor(doc, key_value)
#     nest_data = nest.extract_all_data()

#     print('####################################3')
#     # print('first_data:', data)
#     data = ext.remove_duplication(data)
#     final_data = post_process(data, key_value)
#     print('#######################################3')
#     print('nest_data', nest_data)
#     final_data_keys = [f[0] for f in final_data]
#     print('final_data_keyus', final_data_keys)
#     not_nested_key_value = [k_v for k_v in key_value if (not k_v['extract_all_json']) and (k_v['second_key']!=[])]
#     print('not_nexted_key_value', not_nested_key_value)
#     for ele in not_nested_key_value:
#         if ele['key'] not in final_data_keys:
#             final_data_keys.append([ele['key'], '', '', 0])

#     #### type1)
#     # for k, v in nest_data.items():
#     #     v_as_str = json.dumps(v, ensure_ascii=False)  # v를 JSON 문자열로 변환
#     #     new_d = [k, v_as_str, k , 0]
#     #     final_data.append(new_d)
#     #### type2)
#     for k, v in nest_data.items():
#         #v_as_str = json.dumps(v, ensure_ascii=False)  # v를 SON 문자열로 변환
#         for k2, v2 in v.items():
#             new_d = [f"{k} {k2}", v2, k, 0]
#             final_data.append(new_d)
#     print('final_Dtaa:', final_data)
#     return final_data

def run_data_extract2(file, doc_type_id, key_value):
    print('1:run_data_extract')

    doc = Document(file)
    ext = KeyValueExtractor(doc, key_value)
    data = ext.extract_data()

    nest = NestedTableExtractor(doc, key_value)
    nest_data = nest.extract_all_data()

    # print('first_data:', data)
    # data = ext.remove_duplication(data)
    final_data = post_process(data, key_value)
    #### type1)
    for k, v in nest_data.items():
        v_as_str = json.dumps(v, ensure_ascii=False)  # v를 JSON 문자열로 변환
        new_d = [k, v, k , 0]
        final_data.append(new_d)


    print('final_Dtaa:', final_data)
    return final_data

def save_in_db(data, key_value):
    """data 는 [[k,v,k pos], ...] 여기서 k값이

    Args:
        result (_type_): _description_
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

    # 인스턴스 저장
    im_extraction_instance.save()



def get_loan_data():
    print('2:get_key_value_data')
    loan = Loan.objects.order_by('-created_at').first()
    if not loan:
        return {}
    data = {
        'og_file': loan.og_file,
        'developer': loan.developer,
        'constructor': loan.constructor,
        'trustee': loan.trustee,
        'loan_amount': loan.loan_amount,
        'loan_period': loan.loan_period,
        'fee': loan.fee,
        'irr': loan.irr,
        'prepayment_fee': loan.prepayment_fee,
        'overdue_interest_rate': loan.overdue_interest_rate,
        'principal_repayment_type': loan.principal_repayment_type,
        'interest_payment_period': loan.interest_payment_period,
        'deferred_payment': loan.deferred_payment,
        'joint_guarantee_amount': loan.joint_guarantee_amount,
        'lead_arranger': loan.lead_arranger,
        'company': loan.company,
    }
    # print('data=', data)
    return data


from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
import io

# Assuming these are custom utility functions for your use case.
# These should be imported if they exist already.
# from utils import is_doc_file, is_pdf_file, is_hwp_file, convert_to_docx, run_data_extract, convert_pdf_to_docx, extract_first_5_pages

# def process_file(file):
    # """Main handler for processing the file and extracting key-value pairs."""
    # file_url = None
    # result = []
    
    # if is_doc_file(file):
    #     file, file_url = convert_to_docx(file, 'doc')
    #     result = extract_data_from_docx(file)
        
    # elif is_pdf_file(file):
    #     result = extract_data_from_pdf(file)
        
    # elif is_hwp_file(file):
    #     file, file_url = convert_to_docx(file, 'hwp')
    #     result = extract_data_from_docx(file)
        
    # else:
    #     result = extract_data_from_docx(file)
    
    # return result, file_url

# def extract_data_from_docx(docx_file):
#     """Extract key-value data from DOCX files."""
#     content = docx_file.read()
#     return run_data_extract(io.BytesIO(content))

# def extract_data_from_pdf(pdf_file):
#     """Extract key-value data from PDF files by converting them to DOCX."""
#     pdf_content = pdf_file.read()
#     pdf_file_io = io.BytesIO(pdf_content)
    
#     # Extract first 5 pages from PDF and convert to DOCX
#     input_pdf_path = 'input.pdf'
#     output_pdf_path = 'output_first_5_pages.pdf'
    
#     # Save PDF content temporarily
#     with open(input_pdf_path, 'wb') as f:
#         f.write(pdf_content)
        
#     extract_first_5_pages(input_pdf_path, output_pdf_path)
    
#     # Read the converted first 5 pages of PDF
#     with open(output_pdf_path, 'rb') as f:
#         pdf_5_pages_content = f.read()
#     pdf_5_pages_file = io.BytesIO(pdf_5_pages_content)
    
#     docx_file_path = convert_pdf_to_docx(pdf_5_pages_file)
    
#     # Read the converted DOCX and extract data
#     with open(docx_file_path, 'rb') as f:
#         docx_content = f.read()
        
#     return run_data_extract(io.BytesIO(docx_content))





@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser])
def run_generator_data(request):
    # print('########################')
    res_data = get_loan_data()
    return JsonResponse(res_data, safe=False)



@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser])
def run_generator(request):
    # print('########################')
    res_data = get_loan_data()
    # print('data', res_data)
    gen = DocxGenerator(res_data, 3)
    buf, doc = gen.create_document()
    if buf is None:
        return Response({"error": "buf not made"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        response = HttpResponse(buf, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename="res.docx"'
        return response







@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser])
def extract_xl(request):
    if 'file' not in request.FILES:
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    result, file_url = process_file(file)
    
    # response_data = {
    #     "data": result,
    #     "file_url": file_url
    # }
    print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&11')
    print(result)
    print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&22')
    # # Transforming data into a DataFrame
    # columns = [row[0] for row in result]
    # values = [row[1] for row in result]
    vertical_data = [[row[0], row[1]] for row in result]
    # df = pd.DataFrame([values], columns=columns)
    df = pd.DataFrame(vertical_data, columns=['키', '밸류'])

    
    # Save the DataFrame to an Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    # Create a response with the Excel file
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="extracted_data.xlsx"'
    return response


@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser])
def save_key_value(request):
    if request.method == 'POST':
        try:
            data = request.data
            # print(data)
            Loan.objects.create(
                og_file=data.get('og_file'),
                developer=data.get('developer'),
                constructor=data.get('constructor'),
                trustee=data.get('trustee'),
                loan_amount=data.get('loan_amount'),
                loan_period=data.get('loan_period'),
                fee=data.get('fee'),
                irr=data.get('irr'),
                prepayment_fee=data.get('prepayment_fee'),
                overdue_interest_rate=data.get('overdue_interest_rate'),
                principal_repayment_type=data.get('principal_repayment_type'),
                interest_payment_period=data.get('interest_payment_period'),
                deferred_payment=data.get('deferred_payment'),
                joint_guarantee_amount=data.get('joint_guarantee_amount'),
                lead_arranger=data.get('lead_arranger'),
                company=data.get('company'),
            )
            return JsonResponse({'status': 'success', 'res': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# @csrf_exempt
# @api_view(['POST'])
# @parser_classes([MultiPartParser])
# def save_key_value(request):
#     if request.method == 'POST':
#         try:
#             data = request.data
#             print(data)
#             task = save_data_task.delay(data)
#             Task.objects.create(task_id=task.id, status=task.state)
#             return JsonResponse({'status': 'success', 'task_id': task.id})
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)})
#     return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
@api_view(['GET'])
@parser_classes([MultiPartParser])
def get_task_status(request, task_id):
    try:
        task = Task.objects.get(task_id=task_id)
        return JsonResponse({'task_id': task_id, 'status': task.status, 'result': task.result})
    except Task.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Task not found'})


#############################################for og TSExpert

# @csrf_exempt
# @api_view(['POST'])
# @parser_classes([MultiPartParser])
# def extract_key_value(request):
#     """API endpoint for extracting key-value pairs from a file."""
#     if 'doc' not in request.FILES:
#         return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
    
#     file = request.FILES['doc']
    
#     result, file_url = process_file(file)
    
#     response_data = {
#         "data": result,
#         "file_url": file_url
#     }
#     return JsonResponse(response_data, safe=False)

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
    result = run_data_extract2(io.BytesIO(content), doc_type_id, key_value)
    save_in_db(result, key_value)


    
    return result, {"file_url": file_url}, None

@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser])
def extract_key_value(request):
    """API endpoint for extracting key-value pairs from a file."""
    result, file_url_response, error = process_file(request)
    if error:
        return Response(file_url_response, status=error)

    response_data = {
        "data": result,
        "file_url": file_url_response.get('file_url')
    }
    return JsonResponse(response_data, safe=False)


@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser])
def extract_term_sheet(request):
    """API endpoint for extracting term sheet data."""
    result, file_url_response, error = process_file(request)
    if error:
        return Response(file_url_response, status=error)
    
    response_data = {}
    for title, ele1, ele2, ele3 in result:
        response_data[title] = ele1
    
    return JsonResponse([response_data], safe=False)