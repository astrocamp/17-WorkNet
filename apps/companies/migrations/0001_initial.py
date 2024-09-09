# Generated by Django 5.1 on 2024-08-29 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Company",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("tel", models.CharField(max_length=15)),
                ("url", models.URLField()),
                ("address", models.CharField(max_length=300)),
                ("describe", models.TextField()),
                ("total_headcount", models.IntegerField()),
                ("name", models.CharField(max_length=200)),
                ("email", models.EmailField(max_length=254)),
                ("owner_tel", models.CharField(max_length=15)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(default=None, null=True)),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["deleted_at"],
                        name="companies_c_deleted_99a40f_idx",
                    )
                ],
            },
        ),
    ]
