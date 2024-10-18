from django.db import models

# class KeyValue(models.Model):
#     id = models.AutoField(primary_key=True)
#     title = models.CharField('문서명', max_length=64, null=True, blank=True)
#     key_values = models.JSONField('키-밸류', default=dict, null=True, blank=True)
#     created_at = models.DateTimeField("생성일자", auto_now_add=True)
#     edited_at = models.DateTimeField("수정일자", auto_now=True)


# class Dictionary(models.Model):
#     class Meta:
#         verbose_name = "사전"
#         verbose_name_plural = "사전"
#     TYPE_CHOICES = [
#         ('string', 'String'),
#         ('name', 'Name'),
#         ('department', 'Department'),
#         ('year', 'Year'),
#         ('number', 'Number'),
#         ('date', 'Date'),
#         ('money', 'Money'),
#         ('percentage', 'Percentage'),
#         ('map', 'Map'),
#         ('company', 'Company'),
#     ]
#     id = models.AutoField(primary_key=True)
#     key = models.CharField(max_length=255, null=True, blank=True)
#     type = models.CharField(max_length=50,  choices=TYPE_CHOICES, null=True, blank=True, default='string')
#     is_table = models.BooleanField(default=True)
#     extract_all_json = models.BooleanField(default=False)
#     # extract_second_key = models.BooleanField(default=False)
#     second_key = models.CharField(max_length=600, null=True, blank=True, default="[]")
#     #synonym_priority = models.CharField(max_length=255, null=T/rue, blank=True)
#     synonym_all = models.CharField(max_length=600, null=True, blank=True, default="[]")
#     synonym_pattern = models.CharField(max_length=255, null=True, blank=True, default="[]")
#     sp_word = models.CharField(max_length=255, null=True, blank=True)
#     value = models.CharField(max_length=255,null=True, blank=True, default="[]")
#     split = models.CharField(max_length=255,null=True, blank=True, default="[]")
#     map = models.CharField(max_length=255, null=True, blank=True, default="{}")
#     in_use = models.BooleanField(default=True)
    
#     def __str__(self):
#         return f'{self.key}'
    



#######################################UpdatedDictionary20241017####################################################



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
    trustee = models.CharField('시탁사', max_length=255, null=True, blank=True)
    repay_method = models.CharField('상환방법', max_length=255, null=True, blank=True)
    overdue_interest = models.CharField('연체가산금리', max_length=255, null=True, blank=True)
    loan_amount = models.CharField('대출금액', max_length=255, null=True, blank=True)
    lead_arranger = models.CharField('금융주관사', max_length=255, null=True, blank=True)
    loan_period = models.CharField('대출기간', max_length=255, null=True, blank=True)
    disburse_method = models.CharField('인출방법', max_length=255, null=True, blank=True)
    interest_payment_method = models.CharField('이자지급방법', max_length=255, null=True, blank=True)
    early_repay_fee = models.CharField('조기상환수수료', max_length=255, null=True, blank=True)
    finance_diagram = models.ImageField(upload_to='images/finance_diagram', null=True, blank=True, verbose_name="금융구조도")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일자")
    edited_at = models.DateTimeField(auto_now=True, verbose_name="수정일자")



##########################################################################################





# class Loan(models.Model):
#     class Meta:
#         verbose_name = "Job 로그"
#         verbose_name_plural = "Job 로그"
#     id = models.AutoField(primary_key=True)
#     og_file = models.CharField('파일명', max_length=255)
#     developer = models.CharField('시행사', max_length=255, null=True, blank=True)
#     constructor = models.CharField('시공사', max_length=255, null=True, blank=True)
#     trustee = models.CharField('신탁사', max_length=255, null=True, blank=True)
#     loan_amount = models.CharField('당사여신금액', max_length=255, null=True, blank=True)
#     loan_period = models.CharField('대출기간', max_length=255, null=True, blank=True)
#     fee = models.CharField('수수료', max_length=255, null=True, blank=True)
#     irr = models.CharField('IRR', max_length=255, null=True, blank=True)
#     prepayment_fee = models.CharField('중도상환수수료', max_length=255, null=True, blank=True)
#     overdue_interest_rate = models.CharField('연체이자율', max_length=255, null=True, blank=True)
#     principal_repayment_type = models.CharField('원금상환유형', max_length=255, null=True, blank=True)
#     interest_payment_period = models.CharField('이자상환기한', max_length=255, null=True, blank=True)
#     deferred_payment = models.CharField('상환후불여부', max_length=255, null=True, blank=True)
#     joint_guarantee_amount = models.CharField('연대보증금액', max_length=255, null=True, blank=True)
#     lead_arranger = models.CharField('금융주간사', max_length=255, null=True, blank=True)
#     company = models.CharField('회사', max_length=255, null=True, blank=True)
#     created_at = models.DateTimeField("생성일자", auto_now_add=True)
#     edited_at = models.DateTimeField("수정일자", auto_now=True)

#     def __str__(self):
#         return f'{self.company} - {self.developer}'

# class Template(models.Model):
#     class Meta:
#         verbose_name = "템플릿 (template)"
#         verbose_name_plural = "템플릿 (template)"
#         db_table = 'template'
#     CONTRACT_TYPE = [('투자신청의견서', '투자신청의견서'), ('신탁계약서', '신탁계약서'),('전담중개업무계약서','전담중개업무계약서')]
#     id = models.AutoField(primary_key=True)
#     title = models.CharField("파일명", max_length=32)
#     contract_type = models.CharField("계약서 종류", choices=CONTRACT_TYPE, max_length=32, default='신탁계약서')
#     content = models.FileField(upload_to='documents/templates',  verbose_name="파일")
#     created_at = models.DateTimeField("Created At", auto_now_add = True)
#     edited_at = models.DateTimeField("Edited At", auto_now = True)
#     idx_pos = models.JSONField("인덱스 위치", null=True, blank=True,default=list)
#     def __str__(self):
#         return f'[{self.contract_type}] :     {self.content}'



# class Rules(models.Model):
#     class Meta:
#         verbose_name = "조건정의"
#         verbose_name_plural = "조건정의"
#     PAYMENT_OPTION = [('후불', '후불'), ('선불', '선불')]
#     REPAYMENT_TYPE = [('균등분할상환', '균등분할상환'), ('만기일시상환', '만기일시상환')]


#     id = models.AutoField(primary_key=True)
#     template_idx = models.IntegerField("템플릿위치 인덱스", default=0)
#     final_text = models.TextField("결과텍스트", null=True, blank=True)
#     highlight = models.BooleanField("하이라이트 여부", default=False, null=True, blank=True)
 
#     deferred_payment = models.CharField('상환후불여부', max_length=30, choices=PAYMENT_OPTION, null=True, blank=True)
#     principal_repayment_type = models.CharField('원금상환여부', max_length=30, choices=REPAYMENT_TYPE, null=True, blank=True)
#     def __str__(self):
#         return f'{self.template_idx}______________{self.final_text}'




class Task(models.Model):
    task_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50)
    result = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



