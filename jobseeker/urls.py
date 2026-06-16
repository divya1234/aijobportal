from django.urls import path
from . import views

urlpatterns = [

    path('register/', views.register, name='register'),
    path('jobseeker_profile/', views.jobseeker_profile, name='jobseeker_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile')
]