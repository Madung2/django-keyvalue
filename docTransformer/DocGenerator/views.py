from django.shortcuts import render
from django.http import JsonResponse,  HttpResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from .services.generator import DocxGenerator
from TsExpert.models import IMExtraction
from django.db import models






# Static IM파일 기준:DB 변경되면 수정되야함
# def get_data(doc_type):
#     # IMExtraction 모델에서 가장 최근 레코드를 가져옵니다.
#     latest_record = IMExtraction.objects.last()
#     if not latest_record:
#         return None  # 만약 레코드가 없다면 None을 반환

#     data = {}
#     for field in IMExtraction._meta.fields:
#         # 이미지 필드는 제외
#         if isinstance(field, models.ImageField):
#             continue  # 이미지 필드를 건너뜁니다.

#         field_name = field.name  # 필드 이름
#         field_value = getattr(latest_record, field_name)  # 해당 레코드에서 필드 값 가져오기
#         data[field_name] = field_value
    
#     return data
def get_data(doc_type):
    # IMExtraction 모델에서 가장 최근 레코드를 가져옵니다.
    latest_record = IMExtraction.objects.last()
    if not latest_record:
        return None  # 만약 레코드가 없다면 None을 반환

    data = {}
    for field in IMExtraction._meta.fields:
        field_name = field.name  # 필드 이름
        field_value = getattr(latest_record, field_name)  # 해당 레코드에서 필드 값 가져오기
        
        if isinstance(field, models.ImageField):
            # For image fields, you can return the URL if available
            if field_value:
                field_value = field_value.url  # URL을 반환 (이미지의 경우)
            else:
                field_value = None  # 이미지가 없는 경우 None 처리

        data[field_name] = field_value
    
    return data
#######################################################




# Create your views here.
@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser])
def run_generator(request):

    doc_type = request.data.get('document_type', 3)
    data = get_data(doc_type)

    gen = DocxGenerator(data)
    buf = gen.gen_buf
    if buf is None:
        return Response({"error": "buf not made"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        response = HttpResponse(buf, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename="res.docx"'
        return response

