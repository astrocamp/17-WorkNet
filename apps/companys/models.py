from django.db import models


# Create your models here.
class Company(models.Model):
    title = models.CharField(max_length=200)
    tel = models.CharField(max_length=15)
    url = models.URLField()
    address = models.CharField(max_length=300)
    describe = models.TextField()
    total_headcount = models.IntegerField()
    name = models.CharField(max_length=200)
    email = models.EmailField()
    owner_tel = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(default=None, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["deleted_at"]),
        ]
