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

    path('reject/<int:request_id>/',
         views.reject_request,
         name='reject_request'),

    path('deliver/<int:request_id>/',
         views.confirm_delivery,
         name='confirm_delivery'),

    path('quotation/<int:request_id>/',
         views.add_quotation,
         name='add_quotation'),

    path('deliveries/',
         views.storesman_dashboard,
         name='delivery_dashboard'),

    path('link-item/<int:request_id>/',
         views.link_item,
         name='link_item'),
]