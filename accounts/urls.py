from django.urls import path
from . import views

urlpatterns = [

    path('',
         views.accounts_dashboard,
         name='accounts_dashboard'),

    path('request/<int:request_id>/',
         views.request_detail,
         name='request_detail'),

    path('payments/',
         views.payments,
         name='accounts_payments'),

    path('payments/upload/<int:request_id>/',
         views.upload_payment_proof,
         name='upload_payment_proof'),
]