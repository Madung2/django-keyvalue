from django.db import models

class KeyValue(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField('문서명', max_length=64, null=True, blank=True)
    key_values = models.JSONField('키-밸류', default=dict, null=True, blank=True)
    created_at = models.DateTimeField("생성일자", auto_now_add=True)
    edited_at = models.DateTimeField("수정일자", auto_now=True)


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