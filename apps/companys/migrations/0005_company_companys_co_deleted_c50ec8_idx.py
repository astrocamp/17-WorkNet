# Generated by Django 5.1 on 2024-08-28 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companys', '0004_alter_company_updated_at'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='company',
            index=models.Index(fields=['deleted_at'], name='companys_co_deleted_c50ec8_idx'),
        ),
    ]
