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


    
class IMExtractionAdmin(admin.ModelAdmin):
    list_display = ('id', 'borrower', 'trustee', 'loan_amount', 'loan_period', 'created_at')
    list_display_links =('borrower', 'trustee', 'loan_amount', 'loan_period')
    class Meta:
        verbose_name = "IM 추출 내역"
        verbose_name_plural = "IM 추출 내역"

    



admin.site.register(ExtractDictionary, ExtractDictionaryAdmin)
admin.site.register(DocumentType, DocumentTypeAdmin)
admin.site.register(PrimaryExtractedValue, PrimaryExtractedValueAdmin)
admin.site.register(IMExtraction, IMExtractionAdmin)