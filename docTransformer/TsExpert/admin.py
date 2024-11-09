from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import ExtractDictionary, DocumentType, PrimaryExtractedValue, IMExtraction

from django.utils.html import format_html 


def in_use_active(modeladmin, request, queryset):
    for obj in queryset:
        obj.in_use = not obj.in_use
        obj.save()
in_use_active.short_description = "사용 여부 변경"

########################################################################

class DocumentTypeAdmin(admin.ModelAdmin):
    list_display =('id', 'type_name', 'type_name_kor', 'created_at', 'edited_at')
    list_display_links = ('type_name', 'type_name_kor')
    class Meta:
        verbose_name = '문서타입'
        verbose_name_plural = '문서타입'
    
class ExtractDictionaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_document_type_name_kor', 'user', 'created_at', 'edited_at', 'in_use')
    list_display_links = ('name','get_document_type_name_kor')
    actions = [in_use_active]

    def get_document_type_name_kor(self, obj):
        return obj.document_type.type_name_kor

    # Set the column name in the admin page
    get_document_type_name_kor.short_description = '문서 타입(한국어)'
    class Meta:
        verbose_name = "사전"
        verbose_name_plural = "사전"
    formfield_overrides = {
        models.JSONField: {'widget': Textarea(attrs={'rows': 50, 'cols': 240})},
    }


class PrimaryExtractedValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'document_type', 'value_type', 'key', 'text_value', 'created_at')
    list_display_links = ('document_type', 'value_type', 'key', 'text_value')
    class Meta:
        verbose_name = '추출 키-밸류'
        verbose_name_plural = '추출 키-밸류'


    
# class IMExtractionAdmin(admin.ModelAdmin):
#     list_display = ('id', 'borrower', 'trustee', 'loan_amount', 'loan_period', 'created_at')
#     list_display_links =('borrower', 'trustee', 'loan_amount', 'loan_period')
#     class Meta:
#         verbose_name = "IM 추출 내역"
#         verbose_name_plural = "IM 추출 내역"

    

# class IMExtractionAdmin(admin.ModelAdmin):
#     list_display = ('id', 'borrower', 'trustee', 'loan_amount', 'loan_period', 'created_at', 'custom_button')
#     list_display_links = ('borrower', 'trustee', 'loan_amount', 'loan_period')

#     def custom_button(self, obj):
#         return format_html('<a class="button" href="{}">문서 다운로드</a>', '/admin/imextraction/{}/custom_action/'.format(obj.id))
#     custom_button.short_description = 'Custom Button'

#     class Meta:
#         verbose_name = "IM 추출 내역"
#         verbose_name_plural = "IM 추출 내역"

#     # 커스텀 액션을 처리하는 view 생성
#     def get_urls(self):
#         from django.urls import path
#         urls = super().get_urls()
#         custom_urls = [
#             path('imextraction/<int:object_id>/custom_action/', self.admin_site.admin_view(self.custom_action))
#         ]
#         return custom_urls + urls

#     def custom_action(self, request, object_id):
#         # 버튼이 클릭되었을 때 수행할 작업 구현
#         obj = self.get_object(request, object_id)
#         # 여기에 원하는 로직을 추가하세요
#         print('obj_id', object_id)
#         # self.message_user(request, f"{obj.borrower}에 대한 작업이 완료되었습니다.")
#         # return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.http import HttpResponse, HttpResponseRedirect
import requests
import tempfile
import subprocess
import os
class IMExtractionAdmin(admin.ModelAdmin):
    list_display = ('id', 'borrower', 'trustee', 'loan_amount', 'loan_period', 'created_at', 'download_button')
    list_display_links = ('borrower', 'trustee', 'loan_amount', 'loan_period')

    def download_button(self, obj):
        return format_html(
            '<a class="button" href="{}">파일 다운로드</a>',
            reverse('admin:download_docx', args=[obj.id])
        )
    download_button.short_description = 'Download Button'

    # 다운로드를 처리하는 view 추가
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('download/<int:object_id>/', self.admin_site.admin_view(self.download_docx), name='download_docx'),
        ]
        return custom_urls + urls

    # def download_docx(self, request, object_id):
    #     # 여기서 API를 호출하여 DOCX 파일을 다운로드하고 반환
        
    #     api_url = f"http://{request.get_host()}/dg/run_generator/"
    #     response = requests.post(api_url)  # API 호출
        
    #     if response.status_code == 200:
    #         # 받은 파일을 HttpResponse로 전달
    #         docx_file = response.content
    #         response = HttpResponse(docx_file, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    #         response['Content-Disposition'] = f'attachment; filename="generated_file_{object_id}.docx"'
    #         return response
    #     else:
    #         self.message_user(request, "파일 다운로드 실패", level='error')
    #         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# from django.http import HttpResponse, HttpResponseRedirect
# from django.urls import reverse
# from django.utils.html import format_html
# from django.urls import path
# import requests
# import os

# class IMExtractionAdmin(admin.ModelAdmin):
#     list_display = ('id', 'borrower', 'trustee', 'loan_amount', 'loan_period', 'created_at', 'download_button')
#     list_display_links = ('borrower', 'trustee', 'loan_amount', 'loan_period')

#     def download_button(self, obj):
#         return format_html(
#             '<a class="button" href="{}">파일 다운로드</a>',
#             reverse('admin:download_docx', args=[obj.id])
#         )
#     download_button.short_description = 'Download Button'

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('download/<int:object_id>/', self.admin_site.admin_view(self.download_docx), name='download_docx'),
#         ]
#         return custom_urls + urls

    def download_docx(self, request, object_id):
        # API 호출
        api_url = f"http://{request.get_host()}/dg/run_generator/"
        response = requests.post(api_url)

        if response.status_code == 200:
            # 받은 DOCX 파일을 임시 파일로 저장
            print('working')
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp_docx:
                print('working2')
                tmp_docx.write(response.content)
                tmp_docx.flush()

                # unoconv를 사용하여 LibreOffice로 DOCX 파일을 변환
                converted_file_path = tempfile.mktemp(suffix=".docx")
                subprocess.run(['/usr/local/bin/unoconv', '-f', 'docx', '-o', converted_file_path, tmp_docx.name], check=True)
                print('subprocess 작동 성공!!')
                # 변환된 파일을 읽어서 반환
                with open(converted_file_path, 'rb') as converted_file:
                    response = HttpResponse(converted_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    response['Content-Disposition'] = f'attachment; filename="generated_file_{object_id}.docx"'

                # 임시 파일 삭제
                os.remove(tmp_docx.name)
                os.remove(converted_file_path)

            return response
        else:
            self.message_user(request, "파일 다운로드 실패", level='error')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

admin.site.register(ExtractDictionary, ExtractDictionaryAdmin)
admin.site.register(DocumentType, DocumentTypeAdmin)
admin.site.register(PrimaryExtractedValue, PrimaryExtractedValueAdmin)
admin.site.register(IMExtraction, IMExtractionAdmin)