from django.contrib import admin

# Register your models here.
from .models import Company,Industry
admin.site.register(Company)
admin.site.register(Industry)