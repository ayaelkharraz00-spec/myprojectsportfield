
from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.home,              name='home'),
    path('fields/',                       views.terrain_list,      name='terrain_list'),
    path('fields/<int:pk>/',              views.terrain_detail,    name='terrain_detail'),
    path('fields/<int:terrain_pk>/reserve/', views.make_reservation, name='make_reservation'),
    path('calendar/',                     views.calendar_view,     name='calendar'),
    path('my-reservations/',              views.my_reservations,   name='my_reservations'),
    path('cancel/<int:pk>/',              views.cancel_reservation,name='cancel_reservation'),
    path('edit/<int:pk>/',                views.edit_reservation,  name='edit_reservation'),
    path('register/',                     views.register,          name='register'),
]