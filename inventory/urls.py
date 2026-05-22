from django.urls import path
from . import views

urlpatterns = [

    path('', views.inventory_list, name='inventory_list'),

    path('add-stock/', views.add_stock, name='add_stock'),

    path('edit-stock/<int:item_id>/',
         views.edit_stock,
         name='edit_stock'),

    path('delete-stock/<int:item_id>/',
         views.delete_stock,
         name='delete_stock'),


     path(
    'storesman/',
    views.storesman_dashboard,
    name='storesman_dashboard'
),
]