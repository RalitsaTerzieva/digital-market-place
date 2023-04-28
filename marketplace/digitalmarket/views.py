from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from .models import Product

class IndexView(ListView):
    model = Product
    template_name = 'digitalmarket/index.html'
