
from django.urls import path
from .views import IndexView, ProductDetailView

urlpatterns = [
    path("",IndexView.as_view(),name="index"),
    path("detail/<int:pk>",ProductDetailView.as_view(),name='detail'),
    
]
