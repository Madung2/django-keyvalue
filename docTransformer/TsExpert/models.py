from django.db import models



class DocumentType(models.Model):
    class Meta:
        verbose_name="문서타입"
        verbose_name_plural="문서타입"
    id = models.AutoField('아이디', primary_key=True)
    type_name = models.CharField('타입명', max_length=255, null=True, blank=True)
    type_name_kor = models.CharField('한국어 타입명', max_length=255, null=True, blank=True)
    created_at = models.DateTimeField("생성일자", auto_now_add=True)
    edited_at = models.DateTimeField("수정일자", auto_now=True)

    def __str__(self):
        return self.type_name_kor

class ExtractDictionary(models.Model):
    class Meta:
        verbose_name="사전"
        verbose_name_plural = "사전"
    
    id = models.AutoField('아이디', primary_key=True)
    name = models.CharField('사용처명', max_length=255, null=True, blank=True)
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, verbose_name='문서 유형', default=1)
    user = models.CharField('유저', max_length=255, null=True, blank=True)
    dictionary = models.JSONField('딕셔너리', default=list, null=True, blank=True)
    created_at = models.DateTimeField("생성일자", auto_now_add=True)
    edited_at = models.DateTimeField("수정일자", auto_now=True)
    in_use = models.BooleanField('사용여부', default=True)


class PrimaryExtractedValue(models.Model):
    class Meta:
        verbose_name="추출 키-밸류"
        verbose_name_plural="추출 키-밸류"
    VALUE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('table', 'Table'),
        ('image&table', 'Image&Table'),
        ('any', 'Any'),
    ]
    id = models.AutoField(primary_key=True)
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, verbose_name='문서 유형')
    document_name = models.CharField(max_length=255, verbose_name="문서 이름")
    key = models.CharField(max_length=255, verbose_name="추출키")
    value_type = models.CharField(max_length=50, choices=VALUE_TYPE_CHOICES, default='text', verbose_name="추출값 형식")
    text_value = models.TextField(null=True, blank=True, verbose_name="텍스트 추출값")
    image_value = models.ImageField(upload_to='images/', null=True, blank=True, verbose_name="이미지 추출값")
    table_value = models.TextField(null=True, blank=True, verbose_name="테이블 추출값(XML)")
    table_value_images = models.ImageField(upload_to='tables/',null=True, blank=True, verbose_name="테이블 추출값(이미지)")
    user = models.CharField(max_length=255, verbose_name="유저")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일자")
    edited_at = models.DateTimeField(auto_now=True, verbose_name="수정일자")



class IMExtraction(models.Model):
    class Meta:
        verbose_name = "IM 추출 내역"
        verbose_name_plural = "IM 추출 내역"

    id = models.AutoField(primary_key=True)

    borrower = models.CharField('차주사', max_length=255, null=True, blank=True)
    trustee = models.CharField('신탁사', max_length=255, null=True, blank=True)
    repay_method = models.CharField('상환방법', max_length=255, null=True, blank=True)
    overdue_interest = models.CharField('연체가산금리', max_length=255, null=True, blank=True)
    loan_amount = models.CharField('대출금액', max_length=255, null=True, blank=True)
    lead_arranger = models.CharField('금융주관사', max_length=255, null=True, blank=True)
    loan_period = models.CharField('대출기간', max_length=255, null=True, blank=True)
    disburse_method = models.CharField('인출방법', max_length=255, null=True, blank=True)
    interest_payment_method = models.CharField('이자지급방법', max_length=255, null=True, blank=True)
    early_repay_fee = models.CharField('조기상환수수료', max_length=255, null=True, blank=True)
    finance_diagram = models.ImageField(upload_to='images/finance_diagram', null=True, blank=True, verbose_name="금융구조도")
    procure_amount = models.TextField('조달금액', null=True, blank=True)
    fund_execution = models.TextField('자금조달및집행', null=True, blank=True)
    dev_plan = models.TextField('사업부지개발계획', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일자")
    edited_at = models.DateTimeField(auto_now=True, verbose_name="수정일자")




class Task(models.Model):
    task_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50)
    result = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



