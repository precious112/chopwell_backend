from django.urls import path,include
from . import views as p_views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


urlpatterns = [
    path('create-food/',p_views.CreateFood.as_view(),name='create-food'),
    path('list-vendor-foods/<slug:username>/',p_views.ListVendorFoods.as_view(),name='list-vendor-foods'),
    path('detail-food/<int:pk>/',p_views.DetailFood.as_view(),name='detail-food'),
    path('delete-food/<int:pk>/',p_views.DeleteFood.as_view(),name='delete-food'),
    path('update-food/<int:pk>/',p_views.CreateFood.as_view(),name='create-food'),
    path('pay-vendor/<slug:username1>/<slug:username2>/<int:id>/<int:orders>/',p_views.pay_vendor,name='pay-vendor'),
    path('verify-payment/<slug:reference>/<slug:transaction_id>/<slug:username1>/<slug:username2>/<int:id>/',p_views.verify_payment,name='verify-payment'),
    path('user-transactions/<slug:username>/',p_views.UserTransactionsAPI.as_view(),name='user-transactions'),
    
    
    ]