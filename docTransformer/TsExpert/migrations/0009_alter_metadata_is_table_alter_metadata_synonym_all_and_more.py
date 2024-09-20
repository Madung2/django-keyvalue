# Generated by Django 5.0.7 on 2024-07-30 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TsExpert', '0008_remove_metadata_map_key_remove_metadata_map_value_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadata',
            name='is_table',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='metadata',
            name='synonym_all',
            field=models.CharField(blank=True, default='[]', max_length=600, null=True),
        ),
        migrations.AlterField(
            model_name='metadata',
            name='synonym_pattern',
            field=models.CharField(blank=True, default='[]', max_length=255, null=True),
        ),
    ]
