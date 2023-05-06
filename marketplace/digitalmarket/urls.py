
from django.urls import path
from django.contrib.auth import views
from .views import *

urlpatterns = [
    path("",IndexView.as_view(),name="index"),
    path("detail/<int:pk>",ProductDetailView.as_view(),name='detail'),
    path("success/",payment_success_view,name="success"),
    path("failed/",payment_failed_view,name='failed'),
    path("api/checkout-session/<int:id>/",create_checkout_session,name='api_checkout_session'),
    path("create/",ProductFormView.as_view(), name='create'),
    path("update/<int:pk>/", ProductUpdateView.as_view(), name='update'),
    path("delete/<int:pk>/", ProductDeleteView.as_view(), name='delete'),
    path("dashboard/", DashboardListView.as_view(), name='dashboard'),
    path("register/",SignupView.as_view(),name='register'),
    path("login/",views.LoginView.as_view(template_name='digitalmarket/login.html'),name='login'),
    path("logout/",views.LogoutView.as_view(template_name='digitalmarket/logout.html'),name='logout'), 
    path("purchases/",PurchasesListView.as_view(),name="purchases"),   
]
