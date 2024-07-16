from django.db import models

class KeyValue(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField('문서명', max_length=64, null=True, blank=True)
    key_values = models.JSONField('키-밸류', default=dict, null=True, blank=True)
    created_at = models.DateTimeField("생성일자", auto_now_add=True)
    edited_at = models.DateTimeField("수정일자", auto_now=True)