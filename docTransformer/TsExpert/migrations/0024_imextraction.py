# Generated by Django 5.1.2 on 2024-10-18 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TsExpert', '0023_extractdictionary_document_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='IMExtraction',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('borrower', models.CharField(blank=True, max_length=255, null=True, verbose_name='차주사')),
                ('trustee', models.CharField(blank=True, max_length=255, null=True, verbose_name='시탁사')),
                ('repay_method', models.CharField(blank=True, max_length=255, null=True, verbose_name='상환방법')),
                ('overdue_interest', models.CharField(blank=True, max_length=255, null=True, verbose_name='연체가산금리')),
                ('loan_amount', models.CharField(blank=True, max_length=255, null=True, verbose_name='대출금액')),
                ('lead_arranger', models.CharField(blank=True, max_length=255, null=True, verbose_name='금융주관사')),
                ('loan_period', models.CharField(blank=True, max_length=255, null=True, verbose_name='대출기간')),
                ('disburse_method', models.CharField(blank=True, max_length=255, null=True, verbose_name='인출방법')),
                ('interest_payment_method', models.CharField(blank=True, max_length=255, null=True, verbose_name='이자지급방법')),
                ('early_repay_fee', models.CharField(blank=True, max_length=255, null=True, verbose_name='조기상환수수료')),
                ('finance_diagram', models.ImageField(blank=True, null=True, upload_to='images/finance_diagram', verbose_name='금융구조도')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일자')),
                ('edited_at', models.DateTimeField(auto_now=True, verbose_name='수정일자')),
            ],
            options={
                'verbose_name': 'IM 추출 내역',
                'verbose_name_plural': 'IM 추출 내역',
            },
        ),
    ]
