from django.urls import path
from . import views

urlpatterns = [

    path('',
         views.allocation_list,
         name='allocation_list'),

    path('create/',
         views.create_allocation,
         name='create_allocation'),
]