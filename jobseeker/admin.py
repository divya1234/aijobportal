from django.contrib import admin

# Register your models here.
from .models import JobSeeker,Education,WorkExperience
admin.site.register(JobSeeker),
admin.site.register(Education),
admin.site.register(WorkExperience)