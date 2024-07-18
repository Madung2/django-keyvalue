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



def get_key_value_data():
    latest_key_value = KeyValue.objects.order_by('-created_at').first()
    return latest_key_value.key_values

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