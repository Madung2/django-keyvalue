from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import ExtractDictionary, DocumentType, PrimaryExtractedValue, IMExtraction

from django.utils.html import format_html 
# class KeyValueAdmin(admin.ModelAdmin):
#     list_display = ('title', 'created_at', 'edited_at') 
#     formfield_overrides = {
#         models.JSONField: {'widget': Textarea(attrs={'rows': 20, 'cols': 240})},
#     }

# class LoanAdmin(admin.ModelAdmin):
#     list_display = (
#         'developer', 'constructor', 'trustee', 'loan_amount', 'loan_period',
#         'fee', 'irr', 'prepayment_fee', 'overdue_interest_rate', 'principal_repayment_type',
#         'interest_payment_period', 'deferred_payment', 'joint_guarantee_amount',
#         'lead_arranger', 'company', 'created_at'
#     )
#     class Meta:
#         verbose_name = "Job 로그"
#         verbose_name_plural = "Job 로그"

def in_use_active(modeladmin, request, queryset):
    for obj in queryset:
        obj.in_use = not obj.in_use
        obj.save()
in_use_active.short_description = "사용 여부 변경"

# class DictionaryAdmin(admin.ModelAdmin):
#     list_display = ('key', 'type', 'synonym_all', 'sp_word', 'in_use') 
#     actions = [in_use_active]
#     class Meta:
#         verbose_name = "사전"
#         verbose_name_plural = "사전"

# class RulesAdmin(admin.ModelAdmin):
#     change_form_template = "admin/Rules.html"
#     class Meta:
#         verbose_name = "조건정의"
#         verbose_name_plural = "조건정의"

# class TemplateAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'contract_type', 'download_link', 'created_at', 'edited_at')
#     readonly_fields = ('download_link',)
    

#     def download_link(self, obj):
#         if obj.content:
#             return format_html('<a href="{}" download>{}</a>', obj.content.url, obj.content.name)
#         return "-"
#     download_link.short_description = '파일 다운로드'

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

    



#admin.site.register(KeyValue, KeyValueAdmin)
#admin.site.register(Loan, LoanAdmin)#Job 로그
#admin.site.register(Dictionary, DictionaryAdmin)
#admin.site.register(Template,TemplateAdmin)
# admin.site.register(Rules)
#admin.site.register(Rules, RulesAdmin)


admin.site.register(ExtractDictionary, ExtractDictionaryAdmin)
admin.site.register(DocumentType, DocumentTypeAdmin)
admin.site.register(PrimaryExtractedValue, PrimaryExtractedValueAdmin)
admin.site.register(IMExtraction, IMExtractionAdmin)