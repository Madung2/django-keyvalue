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
from .models import KeyValue
from pdf2docx import Converter
import os
import tempfile
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
    file_extension = os.path.splitext(input_file.name)[1].lower()
    return file_extension == '.pdf'

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
    if is_pdf_file(file):
        print('this is a PDF file')
        # PDF 파일을 읽고 변환
        pdf_content = file.read()
        pdf_file = io.BytesIO(pdf_content)
        docx_file_path = convert_pdf_to_docx(pdf_file)
        
        # 변환된 DOCX 파일을 읽어 run_data_extract에 전달
        with open(docx_file_path, 'rb') as f:
            docx_content = f.read()
        result = run_data_extract(io.BytesIO(docx_content))
    else:
        # DOCX 파일을 바로 처리
        content = file.read()
        result = run_data_extract(io.BytesIO(content))
    
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