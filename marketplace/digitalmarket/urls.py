
from django.urls import path
from .views import IndexView, ProductDetailView,payment_success_view

urlpatterns = [
    path("",IndexView.as_view(),name="index"),
    path("detail/<int:pk>",ProductDetailView.as_view(),name='detail'),
    path("success/",payment_success_view,name="success"),
    
]
