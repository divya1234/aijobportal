from django.urls import path
from . import views

urlpatterns = [

    path('', views.companies, name='companies'),
    path('company_register/', views.company_register, name='company_register'),
    path('company_profile/', views.company_profile, name='company_profile'),
    path('edit_company_profile/',views.edit_company_profile,name='edit_company_profile'),
]