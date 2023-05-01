from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from django.views.generic.edit import CreateView,UpdateView
from django.views.generic.detail import DetailView
from django.views.generic import ListView
from django.conf import settings
from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from .models import Product, OrderDetail
from .forms import ProductForm

import stripe
stripe.api_version = "2020-08-27"
import json


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
    
    
class ProductUpdateView(UpdateView):
    form_class = ProductForm
    model = Product
    template_name_suffix = "_update_form"
    success_url = "/"


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
    order.save()
    
    return render(request, 'digitalmarket/payment_success.html',{'order':order})
        
        
def payment_failed_view(request):
    return render(request, 'digitalmarket/payment_failed.html')