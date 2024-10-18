from django.contrib import admin
from .models import Template, Rules
# Register your
from django.utils.html import format_html  

# def download_link(self, obj):
#     if obj.content:
#         return format_html('<a href="{}" download>{}</a>', obj.content.url, obj.content.name)
#     return "-"
# download_link.short_description = '파일 다운로드'

class TemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'contract_type', 'created_at', 'edited_at')
    #readonly_fields = ('download_link',)
    
class RulesAdmin(admin.ModelAdmin):
    change_form_template = "admin/Rules.html"
    class Meta:
        verbose_name = "조건정의"
        verbose_name_plural = "조건정의"

admin.site.register(Template,TemplateAdmin)
admin.site.register(Rules, RulesAdmin)