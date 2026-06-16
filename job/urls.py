from django.urls import path
from . import views

urlpatterns = [

    path('', views.joblist, name='joblist'),
    path('add_notification/', views.add_notification, name='add_notification'),
    path(
        'get-skills/',
        views.get_skills,
        name='get_skills'
    ),
    path('manage_jobs', views.manage_jobs, name='manage_jobs'),
    path('edit_job/<int:job_id>',views.edit_job, name='edit_job'),
    path('delete_job/<int:job_id>',views.delete_job, name='delete_job'),
    path('job_details/<int:id>/', views.job_details, name='job_details'),
    path('apply_job/<int:id>/', views.apply_job, name='apply_job'),
    path('applications_list', views.applications_list, name='applications_list'),
    path('application/<int:app_id>/<str:status>/',views.update_application_status,name='update_application_status'),
    path('upgrade_job/<int:id>/',views.upgrade_job,name='upgrade_job'),
    path('payment/<int:job_id>/<int:plan_id>/',views.payment_page,name='payment_page'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('application/<int:application_id>/',views.application_detail,name='application_detail'),
    path('my_applications/', views.my_applications, name='my_applications'),
    path('featured_jobs/', views.featured_jobs, name='featured_jobs'),

]   