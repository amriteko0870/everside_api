from unicodedata import name
from django.urls import path,include
from . import views


urlpatterns = [
        path('',views.index,name='index'),
        path('date_filter',views.date_filter,name='date_filter')
        #path('store_data',views.data_store,name='store_data')
]