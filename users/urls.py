from django.urls import path

from . import views

urlpatterns = [

    # LOGIN PAGE
    path('',
         views.login_view,
         name='login'),

    # LOGOUT
    path('logout/',
         views.logout_view,
         name='logout'),
]