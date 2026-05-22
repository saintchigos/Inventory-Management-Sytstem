from django.urls import path
from . import views

urlpatterns = [

    path('',
         views.accounts_dashboard,
         name='accounts_dashboard'),
]