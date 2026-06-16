from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Industry(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
        
class Company(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    def delete(self, *args, **kwargs):
        user = self.user
        super().delete(*args, **kwargs)
        user.delete()
    COMPANY_SIZE_CHOICES = [
        ('1-10', '1-10 Employees'),
        ('11-50', '11-50 Employees'),
        ('51-200', '51-200 Employees'),
        ('201-500', '201-500 Employees'),
        ('501-1000', '501-1000 Employees'),
        ('1001+', '1001+ Employees'),
    ]
    company_name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    industry = models.ForeignKey(
        Industry,
        on_delete=models.CASCADE
    )
    website = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)

    facebook_url = models.URLField(blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    company_size = models.CharField(
                    max_length=20,
                    choices=COMPANY_SIZE_CHOICES
                )
    
    description = models.TextField(blank=True, null=True)

    founded_year = models.PositiveIntegerField(blank=True, null=True)

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name