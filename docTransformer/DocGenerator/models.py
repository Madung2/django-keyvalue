from django.db import models

class Template(models.Model):
    class Meta:
        verbose_name = "템플릿 (template)"
        verbose_name_plural = "템플릿 (template)"
        db_table = 'template'
    CONTRACT_TYPE = [('투자신청의견서', '투자신청의견서'), ('신탁계약서', '신탁계약서'),('전담중개업무계약서','전담중개업무계약서')]
    id = models.AutoField(primary_key=True)
    title = models.CharField("파일명", max_length=32)
    contract_type = models.CharField("계약서 종류", choices=CONTRACT_TYPE, max_length=32, default='신탁계약서') #TsExpert 랑 DocComparex 다 사용될 수 있기 때문에 Foreign key 사용 어려움
    content = models.FileField(upload_to='documents/templates', verbose_name="파일")
    created_at = models.DateTimeField("Created At", auto_now_add = True)
    edited_at = models.DateTimeField("Edited At", auto_now = True)
    idx_pos = models.JSONField("인덱스 위치", null=True, blank=True,default=list)
    def __str__(self):
        return f'[{self.contract_type}] :     {self.content}'


class Rules(models.Model):
    class Meta:
        verbose_name = "조건정의"
        verbose_name_plural = "조건정의"
    PAYMENT_OPTION = [('후불', '후불'), ('선불', '선불')]
    REPAYMENT_TYPE = [('균등분할상환', '균등분할상환'), ('만기일시상환', '만기일시상환')]


    id = models.AutoField(primary_key=True)
    template_idx = models.IntegerField("템플릿위치 인덱스", default=0)
    final_text = models.TextField("결과텍스트", null=True, blank=True)
    highlight = models.BooleanField("하이라이트 여부", default=False, null=True, blank=True)
 
    deferred_payment = models.CharField('상환후불여부', max_length=30, choices=PAYMENT_OPTION, null=True, blank=True)
    principal_repayment_type = models.CharField('원금상환여부', max_length=30, choices=REPAYMENT_TYPE, null=True, blank=True)
    def __str__(self):
        return f'{self.template_idx}______________{self.final_text}'
