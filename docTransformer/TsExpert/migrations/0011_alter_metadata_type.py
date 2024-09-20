# Generated by Django 5.0.7 on 2024-07-30 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TsExpert', '0010_alter_metadata_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadata',
            name='type',
            field=models.CharField(blank=True, choices=[('string', 'String'), ('name', 'Name'), ('department', 'Department'), ('year', 'Year'), ('number', 'Number'), ('date', 'Date'), ('money', 'Money'), ('percentage', 'Percentage'), ('map', 'Map'), ('company', 'Company')], default='string', max_length=50, null=True),
        ),
    ]
