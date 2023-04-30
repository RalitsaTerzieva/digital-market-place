from django.shortcuts import render
from django.urls import reverse

from django.views.generic.detail import DetailView
from django.views.generic import ListView
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Product

import stripe
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
        

@csrf_exempt
def create_checkout_session(request,id):
    request_data = json.load(request.body)
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



