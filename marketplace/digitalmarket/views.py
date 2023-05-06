from django.shortcuts import get_object_or_404, render
from django.urls import reverse,reverse_lazy

from django.db.models import Sum
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.conf import settings
from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from .models import Product, OrderDetail
from .forms import ProductForm,UserRegistrationForm

import stripe
stripe.api_version = "2020-08-27"
import json
import datetime


class IndexView(ListView):
    model = Product
    template_name = 'digitalmarket/index.html'
    

class ProductDetailView(DetailView):
    model = Product
    
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["secret_publish_key"] = settings.STRIPE_PUBLISHABLE_KEY
        return context
        
        
class ProductFormView(CreateView):
    template_name = "digitalmarket/create_product.html"
    form_class = ProductForm
    success_url = "/"
    
class ProductUpdateView(UserPassesTestMixin, UpdateView):
    form_class = ProductForm
    model = Product
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("index")
    
    def test_func(self):
        object = self.get_object()
        return object.seller == self.request.user
    
    
class ProductDeleteView(UserPassesTestMixin,DeleteView):
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy("index")
    
    def test_func(self):
        object = self.get_object()
        return object.seller == self.request.user
    

class PurchasesListView(ListView):
    model = OrderDetail
    template_name = 'digitalmarket/purchases.html'
    
    def get_queryset(self):
        qs = super().get_queryset()
        current_user = self.request.user
        if not current_user.is_staff and not current_user.is_superuser:
            qs = qs.filter(customer_email=self.request.user.email)
            
        return qs


class DashboardListView(ListView):
    model = Product
    template_name = 'digitalmarket/dashboard.html'
    
    def get_queryset(self):
        qs = super().get_queryset()
        current_user = self.request.user
        if not current_user.is_staff and not current_user.is_superuser:
            qs = qs.filter(seller=self.request.user)
        return qs
    
    
class SalesListView(ListView):
    model = OrderDetail
    template_name = 'digitalmarket/sales.html'
    
    def get_queryset(self):
        qs = super().get_queryset()
        current_user = self.request.user
        if not current_user.is_staff and not current_user.is_superuser:
            qs = qs.filter(product__seller=self.request.user)
        return qs
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        
        orders = OrderDetail.objects.filter(product__seller=self.request.user)
        total_sales = orders.aggregate(Sum('amount'))
        
        last_year = datetime.date.today() - datetime.timedelta(days=365)
        data_year = OrderDetail.objects.filter(product__seller=self.request.user,created_on__gt=last_year)
        yearly_sales = data_year.aggregate(Sum('amount'))
        
        last_month = datetime.date.today() - datetime.timedelta(days=30)
        data_month = OrderDetail.objects.filter(product__seller=self.request.user,created_on__gt=last_month)
        monthly_sales = data_month.aggregate(Sum('amount'))
        
        last_week = datetime.date.today() - datetime.timedelta(days=7)
        data_week = OrderDetail.objects.filter(product__seller=self.request.user,created_on__gt=last_week)
        weekly_sales = data_week.aggregate(Sum('amount'))
        
        daily_sales_sums = OrderDetail.objects.filter(product__seller=self.request.user).values('created_on').order_by('created_on').annotate(sum=Sum('amount'))
        
        product_sales_sums = OrderDetail.objects.filter(product__seller=self.request.user).values('product__name').order_by('product__name').annotate(sum=Sum('amount'))
        
        data['total_sales'] = total_sales
        data['yearly_sales'] = yearly_sales
        data['monthly_sales'] = monthly_sales
        data['weekly_sales'] = weekly_sales
        data['daily_sales_sums'] = daily_sales_sums
        data['product_sales_sums'] = product_sales_sums
        
        return data 
    
class SignupView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'digitalmarket/register.html'
    success_url = reverse_lazy("index")

@csrf_exempt
def create_checkout_session(request,id):
    request_data = json.loads(request.body)
    product = Product.objects.get(id=id)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session = stripe.checkout.Session.create(
        customer_email = request_data['email'],
        payment_method_types = ['card'],
        line_items = [
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                         'name': product.name
                    },
                    'unit_amount': int(product.price * 100)
                },
                'quantity': 1,
            }
        ],
        mode = 'payment',
        success_url = request.build_absolute_uri(reverse('success')) + 
        "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url = request.build_absolute_uri(reverse('failed')),
    )
    
    order = OrderDetail()
    order.customer_email = request_data['email']
    order.product = product
    order.stripe_payment_intent = checkout_session['payment_intent']
    order.amount = int(product.price)
    order.save()

    return JsonResponse({'sessionId':checkout_session.id})


def payment_success_view(request):
    session_id = request.GET.get('session_id')
    
    if session_id is None:
        return HttpResponseNotFound()
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.retrieve(session_id)
    order = get_object_or_404(OrderDetail,stripe_payment_intent=session.payment_intent)
    order.has_paid = True
    
    product = Product.objects.get(id=order.product.id)
    product.total_sales_amount = product.total_sales_amount + int(product.price)
    product.total_sales = product.total_sales + 1
    
    product.save()
    order.save()
    
    return render(request, 'digitalmarket/payment_success.html',{'order':order})
        
        
def payment_failed_view(request):
    return render(request, 'digitalmarket/payment_failed.html')