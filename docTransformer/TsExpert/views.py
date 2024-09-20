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
##################################################

from django.shortcuts import render

def render_tsexpert(req):
    context = {
        'HOST': settings.HOST,
        'PORT': settings.PORT
    }
    return render(req, 'TsExpert.html', context)

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
    latest_key_value = KeyValue.objects.order_by('-created_at').first()
    if latest_key_value:
        return latest_key_value.key_values
    print('currently using defalt key values!!!!!!!')
    return default_key_value

def run_data_extract(file):
    key_value = get_key_value_data()
    print(dir(file))
    doc = Document(file)
    ext = KeyValueExtractor(doc, key_value)
    data = ext.extract_data()
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
    content = file.read()
    result = run_data_extract(io.BytesIO(content))
    print('result_data=', result)
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
    df.to_excel(output, index=False)
    output.seek(0)

    # Create a response with the Excel file
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="extracted_data.xlsx"'
    return response