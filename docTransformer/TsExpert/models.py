from django.db import models

class KeyValue(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField('문서명', max_length=64, null=True, blank=True)
    key_values = models.JSONField('키-밸류', default=dict, null=True, blank=True)
    created_at = models.DateTimeField("생성일자", auto_now_add=True)
    edited_at = models.DateTimeField("수정일자", auto_now=True)


class MetaData(models.Model):
    TYPE_CHOICES = [
        ('string', 'String'),
        ('name', 'Name'),
        ('department', 'Department'),
        ('year', 'Year'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('money', 'Money'),
        ('percentage', 'Percentage'),
        ('map', 'Map'),
        ('company', 'Company'),
    ]
    id = models.AutoField(primary_key=True)
    key = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=50,  choices=TYPE_CHOICES, null=True, blank=True, default='string')
    is_table = models.BooleanField(default=True)
    #synonym_priority = models.CharField(max_length=255, null=T/rue, blank=True)
    synonym_all = models.CharField(max_length=600, null=True, blank=True, default="[]")
    synonym_pattern = models.CharField(max_length=255, null=True, blank=True, default="[]")
    sp_word = models.CharField(max_length=255, null=True, blank=True)
    value = models.CharField(max_length=255,null=True, blank=True, default="[]")
    split = models.CharField(max_length=255,null=True, blank=True, default="[]")
    map = models.CharField(max_length=255, null=True, blank=True, default="{}")
    in_use = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.key}'



class Loan(models.Model):
    id = models.AutoField(primary_key=True)
    og_file = models.CharField('파일명', max_length=255)
    developer = models.CharField('시행사', max_length=255, null=True, blank=True)
    constructor = models.CharField('시공사', max_length=255, null=True, blank=True)
    trustee = models.CharField('신탁사', max_length=255, null=True, blank=True)
    loan_amount = models.CharField('당사여신금액', max_length=255, null=True, blank=True)
    loan_period = models.CharField('대출기간', max_length=255, null=True, blank=True)
    fee = models.CharField('수수료', max_length=255, null=True, blank=True)
    irr = models.CharField('IRR', max_length=255, null=True, blank=True)
    prepayment_fee = models.CharField('중도상환수수료', max_length=255, null=True, blank=True)
    overdue_interest_rate = models.CharField('연체이자율', max_length=255, null=True, blank=True)
    principal_repayment_type = models.CharField('원금상환유형', max_length=255, null=True, blank=True)
    interest_payment_period = models.CharField('이자상환기한', max_length=255, null=True, blank=True)
    deferred_payment = models.CharField('상환후불여부', max_length=255, null=True, blank=True)
    joint_guarantee_amount = models.CharField('연대보증금액', max_length=255, null=True, blank=True)
    lead_arranger = models.CharField('금융주간사', max_length=255, null=True, blank=True)
    company = models.CharField('회사', max_length=255, null=True, blank=True)
    created_at = models.DateTimeField("생성일자", auto_now_add=True)
    edited_at = models.DateTimeField("수정일자", auto_now=True)

    def __str__(self):
        return f'{self.company} - {self.developer}'

class Template(models.Model):
    class Meta:
        verbose_name = "템플릿 (template)"
        verbose_name_plural = "템플릿 (template)"
        db_table = 'template'
    CONTRACT_TYPE = [('투자신청의견서', '투자신청의견서'), ('신탁계약서', '신탁계약서'),('전담중개업무계약서','전담중개업무계약서')]
    id = models.AutoField(primary_key=True)
    title = models.CharField("파일명", max_length=32)
    contract_type = models.CharField("계약서 종류", choices=CONTRACT_TYPE, max_length=32, default='신탁계약서')
    content = models.FileField(upload_to='documents/templates',  verbose_name="파일")
    created_at = models.DateTimeField("Created At", auto_now_add = True)
    edited_at = models.DateTimeField("Edited At", auto_now = True)
    idx_pos = models.JSONField("인덱스 위치", null=True, blank=True,default=list)
    def __str__(self):
        return f'[{self.contract_type}] :     {self.content}'



class Rules(models.Model):
    id = models.AutoField(primary_key=True)








