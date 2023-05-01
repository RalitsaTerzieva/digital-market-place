
from django.urls import path
from .views import IndexView, ProductDetailView,ProductFormView, ProductUpdateView,payment_success_view,payment_failed_view,create_checkout_session

urlpatterns = [
    path("",IndexView.as_view(),name="index"),
    path("detail/<int:pk>",ProductDetailView.as_view(),name='detail'),
    path("success/",payment_success_view,name="success"),
    path("failed/",payment_failed_view,name='failed'),
    path("api/checkout-session/<int:id>/",create_checkout_session,name='api_checkout_session'),
    path("create/",ProductFormView.as_view(), name='create'),
    path("update/<int:pk>", ProductUpdateView.as_view(), name='update'),
]
