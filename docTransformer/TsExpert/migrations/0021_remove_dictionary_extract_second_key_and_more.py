# Generated by Django 5.0.7 on 2024-09-12 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TsExpert', '0020_remove_dictionary_second_key_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dictionary',
            name='extract_second_key',
        ),
        migrations.AddField(
            model_name='dictionary',
            name='second_key',
            field=models.CharField(blank=True, default='[]', max_length=600, null=True),
        ),
    ]