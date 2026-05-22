from django.urls import path
from . import views

urlpatterns = [

    path('',
         views.principal_dashboard,
         name='principal_dashboard'),
]