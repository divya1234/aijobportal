from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    
    path('login/', views.user_login, name='login'),
    path('company_dashboard/', views.company_dashboard, name='company_dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    path('', views.home, name='home'),
    path('superadmin_dashboard/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html'
        ),
        name='password_reset'
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    path('toggle_company/<int:company_id>/', views.toggle_company_status, name='toggle_company'),
]