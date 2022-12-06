from django.urls import path,include
from . import views as p_views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.authentication import BasicAuthentication

schema_view = get_schema_view(
   openapi.Info(
      title="Chopwell API",
      default_version='v1',
      description="API description",
      url='https://chopwell.up.railway.app/',
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="preciouskent8@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
   #authentication_classes = [BasicAuthentication]
)


urlpatterns = [
    path('register/', p_views.RegisterAPI.as_view(), name='register'),
    path('verify/', p_views.Verify, name='verify'),
    path('create-password/', p_views.createPassword, name='create-password'),
    path('login/',p_views.LoginAPI.as_view(),name='login'),
    path('forget-password/<str:email>/',p_views.ForgetPassword,name='forget-password'),
    path('get-profile/<slug:username>/',p_views.get_profile,name='get-profile'),
    path('update-profile/<int:pk>/',p_views.UpdateProfile.as_view(),name='update-profile'),
    path('create-profile/<slug:username>/',p_views.create_profile,name='create-profile'),
    path('get-near-vendors/<slug:username>/',p_views.GetNearVendors,name='get-near-vendors'),
    path('get-premium-vendors/<slug:username>/',p_views.GetPremiumVendors,name='get-premium-vendors'),
    path('get-rated-vendors/<int:id>/',p_views.GetRatedVendors,name='get-rated-vendors'),
    path('rate-vendor/<slug:vendor>/<int:rate>/',p_views.RateVendors,name='rate-vendor'),
    path('search-vendor/',p_views.SearchVendor.as_view(),name='search-vendor'),
    path('logout/<slug:username>/',p_views.Logout,name='logout'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]

