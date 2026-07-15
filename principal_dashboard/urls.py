from django.urls import path
from . import views

urlpatterns = [

    path('',
         views.principal_dashboard,
         name='principal_dashboard'),

    path('procurement/',
         views.procurement_audit,
         name='procurement_audit'),

    path('procurement/<int:request_id>/',
         views.request_audit_detail,
         name='request_audit_detail'),

    path('accounts-activity/',
         views.accounts_activity,
         name='accounts_activity'),

    path('allocations/',
         views.allocation_audit,
         name='allocation_audit'),

    path('users/',
         views.user_directory,
         name='user_directory'),
]