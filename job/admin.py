from django.contrib import admin

# Register your models here.
from .models import JobCategory,Skill,FeaturedPlan
admin.site.register(JobCategory)
admin.site.register(Skill)
admin.site.register(FeaturedPlan)
