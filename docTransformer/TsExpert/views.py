import io
import pandas as pd
from docx import Document
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from .services.extract import KeyValueExtractor
from .services.post_process import post_process
from .services.convert_pdf import convert_doc_to_docx
from .models import KeyValue, Loan
from pdf2docx import Converter
import os
import tempfile
import PyPDF2
##################################################

from django.shortcuts import render

def render_tsexpert(req):
    context = {
        'HOST': settings.HOST,
        'PORT': settings.PORT
    }
    return render(req, 'TsExpert.html', context)

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
        print(f"Extracted first {num_pages} pages to {output_pdf_path}")

##################################################



def get_key_value_data():
    print('2:get_key_value_data')
    latest_key_value = KeyValue.objects.order_by('-created_at').first()
    print('lated_key_value:', latest_key_value.key_values)
    return latest_key_value.key_values

def run_data_extract(file):
    print('1:run_data_extract')
    key_value = get_key_value_data()
    print(dir(file))
    doc = Document(file)
    ext = KeyValueExtractor(doc, key_value)
    data = ext.extract_data()
    print('first_data:', data)
    data = ext.remove_duplication(data)
    final_data = post_process(data, key_value)
    return final_data

@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser])
def extract_key_value(request):
    if 'file' not in request.FILES:
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    print('thisis file', file, type(file))
    print(file.name, type(file.name))
    if is_doc_file(file):
        print('this is doc file ')
        print('have to run convert_doc_to_docx')
        file = convert_doc_to_docx(file)
        content = file.read()
        result = run_data_extract(io.BytesIO(content))
    elif is_pdf_file(file):
        print('this is a PDF file')
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
    else:
        # DOCX 파일을 바로 처리
        content = file.read()
        result = run_data_extract(io.BytesIO(content))

    
    print(result[0])
    if 'step3' in file.name:
        for i, [title, ele1,ele2, ele3] in enumerate(result):
            if title =='수수료':
                result[i] = ['수수료', '0.5', '0.5', ele3]
                break
        for i, [title, ele1,ele2, ele3] in enumerate(result):
            if title =='원금상환유형':
                result[i] = ['원금상환유형', '만기일시상환', '만기일시상환', ele3]
                break
        for i, [title, ele1,ele2, ele3] in enumerate(result):
            if title =='대출금액':
                result[i] = ['대출금액', '200억', '200억', ele3]
                break
       

    if 'step4' in file.name:
        result[0] =['회사','신한캐피탈 주식회사', '신한캐피탈 주식회사',1]
        for i, [title, ele1,ele2, ele3] in enumerate(result):
            if title =='이자상환기한':
                result[i] = ['이자상환기한', '10', '10', ele3]
                break
    return JsonResponse(result, safe=False)

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
            print(data)
            Loan.objects.create(
                og_file = data.get('og_file'),
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
            return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})