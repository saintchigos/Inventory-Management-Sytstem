from django.urls import path
from . import views

urlpatterns = [

    path('inventory/excel/',
         views.export_inventory_excel,
         name='export_inventory_excel'),
]