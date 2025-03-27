from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('earthquake-data/', views.earthquake_data, name='earthquake-data'),
]
