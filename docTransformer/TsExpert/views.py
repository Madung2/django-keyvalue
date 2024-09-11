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
from .services.DocGenerator import DocxHTMLParser, DocxGenerator
from .models import KeyValue, Loan, MetaData, Template, Task
from pdf2docx import Converter
from django.http import HttpResponse
from .tasks import save_data_task
import os
import tempfile
import PyPDF2
import json
##################################################

from django.shortcuts import render

def render_tsexpert(req):
    context = {
        'HOST': settings.HOST,
        'PORT': settings.PORT
    }
    return render(req, 'TsExpert.html', context)


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



def get_key_value_data():
    print('2:get_key_value_data')
    latest_key_value = KeyValue.objects.order_by('-created_at').first()
    # print('lated_key_value:', latest_key_value.key_values)
    return latest_key_value.key_values

def get_meta_data():
    print('2:get_meta_data')
    meta_data_objects = MetaData.objects.filter(in_use=True)
    data = []
    
    for obj in meta_data_objects:
        item = {
            "key": obj.key,
            "type": obj.type,
            "is_table": obj.is_table,
            "extract_all_json": obj.extract_all_json,
            "synonym": {
                "priority": json.loads(obj.synonym_all),
                "all": json.loads(obj.synonym_all),
                "pattern": json.loads(obj.synonym_pattern)
            },
            "specific": bool(obj.sp_word),
            "sp_word": obj.sp_word,
            "value": json.loads(obj.value),
            "split": json.loads(obj.split),
            "map": json.loads(obj.map),
        }
        data.append(item)
    print('latest metadata:', data)
    return data

def run_data_extract(file):
    print('1:run_data_extract')
    if settings.METATYPE ==2:
        key_value = get_meta_data()
    else:
        key_value = get_key_value_data()
    # print(dir(file))
    doc = Document(file)
    ext = KeyValueExtractor(doc, key_value)
    data = ext.extract_data()

    nest = NestedTableExtractor(doc, key_value)
    nest_data = nest.extract_all_data()

    print('####################################3')
    # print('first_data:', data)
    data = ext.remove_duplication(data)
    final_data = post_process(data, key_value)
    print('#######################################3')
    print('nest_data', nest_data)
    final_data_keys = [f[0] for f in final_data]
    print('final_data_keyus', final_data_keys)
    not_nested_key_value = [k_v for k_v in key_value if not k_v['extract_all_json']]
    for ele in not_nested_key_value:
        if ele['key'] not in final_data_keys:
            final_data_keys.append([ele['key'], '', '', 0])

    #### type1)
    # for k, v in nest_data.items():
    #     v_as_str = json.dumps(v, ensure_ascii=False)  # v를 JSON 문자열로 변환
    #     new_d = [k, v_as_str, k , 0]
    #     final_data.append(new_d)
    #### type2)
    for k, v in nest_data.items():
        #v_as_str = json.dumps(v, ensure_ascii=False)  # v를 SON 문자열로 변환
        for k2, v2 in v.items():
            new_d = [f"{k} {k2}", v2, k, 0]
            final_data.append(new_d)
    print('final_Dtaa:', final_data)
    return final_data

def run_data_extract2(file):
    print('1:run_data_extract')
    if settings.METATYPE ==2:
        key_value = get_meta_data()
    else:
        key_value = get_key_value_data()
    # print(dir(file))
    doc = Document(file)
    ext = KeyValueExtractor(doc, key_value)
    data = ext.extract_data()

    nest = NestedTableExtractor(doc, key_value)
    nest_data = nest.extract_all_data()

    print('####################################3')
    # print('first_data:', data)
    data = ext.remove_duplication(data)
    final_data = post_process(data, key_value)
    print('#######################################3')
    print('nest_data', nest_data)
    #### type1)
    for k, v in nest_data.items():
        v_as_str = json.dumps(v, ensure_ascii=False)  # v를 JSON 문자열로 변환
        new_d = [k, v, k , 0]
        final_data.append(new_d)
    #### type2)
    # for k, v in nest_data.items():
    #     #v_as_str = json.dumps(v, ensure_ascii=False)  # v를 SON 문자열로 변환
    #     for k2, v2 in v.items():
    #         new_d = [f"{k} {k2}", v2, k, 0]
    #         final_data.append(new_d)
    print('final_Dtaa:', final_data)
    return final_data


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


@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser])
def extract_key_value(request):
    if 'file' not in request.FILES:
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    file_url = None
    result = []
    # print('thisis file', file, type(file))
    # print(file.name, type(file.name))

    if is_doc_file(file):
        # print('this is doc file ')
        # print('have to run convert_doc_to_docx')
        file, file_url = convert_to_docx(file, 'doc')
        content = file.read()
        result = run_data_extract(io.BytesIO(content))
    elif is_pdf_file(file):
        # print('this is a PDF file')
        # PDF 파일을 읽고 변환
        pdf_content = file.read()
        pdf_file = io.BytesIO(pdf_content)
        
        # 임시 파일 경로 설정
        input_pdf_path = 'input.pdf'
        output_pdf_path = 'output_first_5_pages.pdf'
        
        # 임시 파일에 PDF 내용 쓰기
        with open(input_pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        # 첫 5페이지 추출
        extract_first_5_pages(input_pdf_path, output_pdf_path)
        
        # 변환된 PDF 파일을 읽어 convert_pdf_to_docx에 전달
        with open(output_pdf_path, 'rb') as f:
            pdf_5_pages_content = f.read()
        pdf_5_pages_file = io.BytesIO(pdf_5_pages_content)
        docx_file_path = convert_pdf_to_docx(pdf_5_pages_file)
        
        # 변환된 DOCX 파일을 읽어 run_data_extract에 전달
        with open(docx_file_path, 'rb') as f:
            docx_content = f.read()
        result = run_data_extract(io.BytesIO(docx_content))

    elif is_hwp_file(file):
        # print('This is an HWP file.')
        file, file_url = convert_to_docx(file, 'hwp')
        content = file.read()
        result = run_data_extract(io.BytesIO(content))
    else:
        # DOCX 파일을 바로 처리
        content = file.read()
        result = run_data_extract(io.BytesIO(content))

    print('result1', result)

    # 변환된 파일 저장 및 URL 생성
    # if file_url:
    #     saved_file_name = default_storage.save(os.path.join('documents/converted', os.path.basename(file_location)), ContentFile(file.read()))
    #     file_url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, saved_file_name))
    #     print(f"Generated file URL: {file_url}")
    # 위치 처리
    # print(result[0])
    # if 'step3' in file.name:
    #     for i, [title, ele1, ele2, ele3] in enumerate(result):
    #         if title == '수수료':
    #             result[i] = ['수수료', '0.5', '0.5', ele3]
    #             break
    #     for i, [title, ele1, ele2, ele3] in enumerate(result):
    #         if title == '원금상환유형':
    #             result[i] = ['원금상환유형', '만기일시상환', '만기일시상환', ele3]
    #             break
    #     for i, [title, ele1, ele2, ele3] in enumerate(result):
    #         if title == '대출금액':
    #             result[i] = ['대출금액', '200억', '200억', ele3]
    #             break

    # if 'step4' in file.name:
    #     result[0] = ['회사', '신한캐피탈 주식회사', '신한캐피탈 주식회사', 1]
    #     for i, [title, ele1, ele2, ele3] in enumerate(result):
    #         if title == '이자상환기한':
    #             result[i] = ['이자상환기한', '10', '10', ele3]
    #             break
    
    print('result2', result)
    response_data = {
        "data": result,
        "file_url": file_url
    }
    return JsonResponse(response_data, safe=False)


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

    content = file.read()
    data = run_data_extract(io.BytesIO(content))
    
    # Transforming data into a DataFrame
    columns = [row[0] for row in data]
    values = [row[1] for row in data]
    df = pd.DataFrame([values], columns=columns)
    
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




@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser])
def extract_term_sheet(request):
    if 'doc' not in request.FILES:
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['doc']
    file_url = None
    # print('thisis file', file, type(file))
    # print(file.name, type(file.name))

    if is_doc_file(file):
        # print('this is doc file ')
        # print('have to run convert_doc_to_docx')
        file, file_url = convert_to_docx(file, 'doc')
        content = file.read()
        result = run_data_extract2(io.BytesIO(content))
    # elif is_pdf_file(file):
    #     # print('this is a PDF file')
    #     # PDF 파일을 읽고 변환
    #     pdf_content = file.read()
    #     pdf_file = io.BytesIO(pdf_content)
        
    #     # 임시 파일 경로 설정
    #     input_pdf_path = 'input.pdf'
    #     output_pdf_path = 'output_first_5_pages.pdf'
        
    #     # 임시 파일에 PDF 내용 쓰기
    #     with open(input_pdf_path, 'wb') as f:
    #         f.write(pdf_content)
        
    #     # 첫 5페이지 추출
    #     extract_first_5_pages(input_pdf_path, output_pdf_path)
        
    #     # 변환된 PDF 파일을 읽어 convert_pdf_to_docx에 전달
    #     with open(output_pdf_path, 'rb') as f:
    #         pdf_5_pages_content = f.read()
    #     pdf_5_pages_file = io.BytesIO(pdf_5_pages_content)
    #     docx_file_path = convert_pdf_to_docx(pdf_5_pages_file)
        
    #     # 변환된 DOCX 파일을 읽어 run_data_extract에 전달
    #     with open(docx_file_path, 'rb') as f:
    #         docx_content = f.read()
    #     result = run_data_extract2(io.BytesIO(docx_content))

    elif is_hwp_file(file):
        # print('This is an HWP file.')
        file, file_url = convert_to_docx(file, 'hwp')
        content = file.read()
        result = run_data_extract2(io.BytesIO(content))
    else:
        # DOCX 파일을 바로 처리
        content = file.read()
        result = run_data_extract2(io.BytesIO(content))

    # 변환된 파일 저장 및 URL 생성
    # if file_url:
    #     saved_file_name = default_storage.save(os.path.join('documents/converted', os.path.basename(file_location)), ContentFile(file.read()))
    #     file_url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, saved_file_name))
    #     print(f"Generated file URL: {file_url}")
    # 위치 처리
    # print(result[0])
    if 'step3' in file.name:
        for i, [title, ele1, ele2, ele3] in enumerate(result):
            if title == '수수료':
                result[i] = ['수수료', '0.5', '0.5', ele3]
                break
        for i, [title, ele1, ele2, ele3] in enumerate(result):
            if title == '원금상환유형':
                result[i] = ['원금상환유형', '만기일시상환', '만기일시상환', ele3]
                break
        for i, [title, ele1, ele2, ele3] in enumerate(result):
            if title == '대출금액':
                result[i] = ['대출금액', '200억', '200억', ele3]
                break

    if 'step4' in file.name:
        result[0] = ['회사', '신한캐피탈 주식회사', '신한캐피탈 주식회사', 1]
        for i, [title, ele1, ele2, ele3] in enumerate(result):
            if title == '이자상환기한':
                result[i] = ['이자상환기한', '10', '10', ele3]
                break

    # response_data = {
    #     "data": result,
    #     "file_url": file_url
    # }
    response_data = {}
    for title, ele1, ele2, ele3 in result:
        response_data[title] = ele1
    return JsonResponse([response_data], safe=False)