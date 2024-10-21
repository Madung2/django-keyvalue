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
from .services.insert_xml_table import insert_multiple_tables_into_placeholders




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


def get_placeholder_table_dict(data):
    new_dict= {}
    for k,v in data.items():
        if type(v)==str and v.startswith('<w:'):
            print('newdict', k )
            new_dict[k]= v
    return new_dict

# Create your views here.
@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser])
def run_generator(request):

    doc_type = request.data.get('document_type', 3)
    data = get_data(doc_type)

    # DocxGenerator는 xml 데이터 처리를 못함.
    gen = DocxGenerator(data)


    buf = gen.gen_buf
    if buf is None:
        return Response({"error": "buf not made"}, status=status.HTTP_400_BAD_REQUEST)
    # 임시 파일에 생성된 DOCX 파일 저장
    temp_docx_path = 'generated_temp.docx'
    with open(temp_docx_path, 'wb') as temp_file:
        temp_file.write(buf.getvalue())

    # insert_multiple_tables_into_placeholders를 사용해 테이블 삽입
    output_path = 'final_output.docx'
    
    placeholder_table_dict = get_placeholder_table_dict(data)
    print('placeholder::::', len(placeholder_table_dict), [k for k, v in placeholder_table_dict.items()])
    if placeholder_table_dict:
        insert_multiple_tables_into_placeholders(temp_docx_path, placeholder_table_dict, output_path)

    # 최종 결과물을 response로 반환
        print('??????')
        with open(output_path, 'rb') as final_file:
            response = HttpResponse(final_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = 'attachment; filename="res6.docx"'
            return response
    return

