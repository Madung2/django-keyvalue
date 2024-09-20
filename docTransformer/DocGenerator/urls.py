from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import * 
urlpatterns = [
    # path('', render_tsexpert, name='render_tsexpert'),
    # path('gen/', render_docGenerator, name='render_docGenerator'),
    # path('extract_key_value/', extract_key_value, name='extract_key_value'),
    # path('extract_xl/', extract_xl, name='extract_xl'),
    # path('save_key_value/', save_key_value, name='save_key_value'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


class Template(models.Model):
    class Meta:
        verbose_name = "템플릿 (template)"
        verbose_name_plural = "템플릿 (template)"
        db_table = 'template'
    CONTRACT_TYPE = [('신청의견서', '신청의견서'),('신탁계약서', '신탁계약서'),('전담중개업무계약서','전담중개업무계약서')]
    id = models.AutoField(primary_key=True)
    title = models.CharField("파일명", max_length=32)
    contract_type = models.CharField("계약서 종류", choices=CONTRACT_TYPE, max_length=32, default='신탁계약서')
    content = models.FileField(upload_to='documents/templates',  verbose_name="파일")
    created_at = models.DateTimeField("Created At", auto_now_add = True)
    edited_at = models.DateTimeField("Edited At", auto_now = True)
    idx_pos = models.JSONField("인덱스 위치", null=True, blank=True,default=list)
    def __str__(self):
        return f'[{self.contract_type}] :     {self.content}'
