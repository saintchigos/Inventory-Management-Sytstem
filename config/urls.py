from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    path('admin/', admin.site.urls),

    # LOGIN PAGE FIRST
    path('', include('users.urls')),

    # INVENTORY
    path('inventory/',
         include('inventory.urls')),

    # PROCUREMENT
    path('procurement/',
         include('procurement.urls')),

    # ACCOUNTS
    path('accounts/',
         include('accounts.urls')),

    # PRINCIPAL
    path('principal/',
         include('principal_dashboard.urls')),

    # ALLOCATIONS
    path('allocations/',
         include('allocations.urls')),

    # REPORTS
    path('reports/',
         include('reports.urls')),
]