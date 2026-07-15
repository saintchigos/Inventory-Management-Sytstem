from django.urls import path
from . import views

urlpatterns = [

    path('inventory/excel/',
         views.export_inventory_excel,
         name='export_inventory_excel'),

    path('allocations/excel/',
         views.export_allocations_excel,
         name='export_allocations_excel'),
]