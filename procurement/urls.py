from django.urls import path
from . import views

urlpatterns = [

    path('',
         views.procurement_list,
         name='procurement_list'),

    path('create/',
         views.create_procurement_request,
         name='create_procurement'),

    path('approve/<int:request_id>/',
         views.approve_request,
         name='approve_request'),

    path('deliver/<int:request_id>/',
         views.confirm_delivery,
         name='confirm_delivery'),
]