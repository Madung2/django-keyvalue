# Generated by Django 5.0.7 on 2024-07-29 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TsExpert', '0003_alter_keyvalue_key_values'),
    ]

    operations = [
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('og_file', models.CharField(max_length=255, verbose_name='파일명')),
                ('developer', models.CharField(blank=True, max_length=255, null=True, verbose_name='시행사')),
                ('constructor', models.CharField(blank=True, max_length=255, null=True, verbose_name='시공사')),
                ('trustee', models.CharField(blank=True, max_length=255, null=True, verbose_name='신탁사')),
                ('loan_amount', models.BigIntegerField(blank=True, null=True, verbose_name='당사여신금액')),
                ('loan_period', models.IntegerField(blank=True, null=True, verbose_name='대출기간')),
                ('fee', models.BigIntegerField(blank=True, null=True, verbose_name='수수료')),
                ('irr', models.FloatField(blank=True, null=True, verbose_name='IRR')),
                ('prepayment_fee', models.FloatField(blank=True, null=True, verbose_name='중도상환수수료')),
                ('overdue_interest_rate', models.FloatField(blank=True, null=True, verbose_name='연체이자율')),
                ('principal_repayment_type', models.CharField(blank=True, max_length=255, null=True, verbose_name='원금상환유형')),
                ('interest_payment_period', models.IntegerField(blank=True, null=True, verbose_name='이자상환기한')),
                ('deferred_payment', models.CharField(blank=True, max_length=255, null=True, verbose_name='상환후불여부')),
                ('joint_guarantee_amount', models.FloatField(blank=True, null=True, verbose_name='연대보증금액')),
                ('lead_arranger', models.CharField(blank=True, max_length=255, null=True, verbose_name='금융주간사')),
                ('company', models.CharField(blank=True, max_length=255, null=True, verbose_name='회사')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일자')),
                ('edited_at', models.DateTimeField(auto_now=True, verbose_name='수정일자')),
            ],
        ),
    ]
