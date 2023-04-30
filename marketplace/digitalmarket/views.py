from django.shortcuts import render

from django.views.generic.detail import DetailView
from django.views.generic import ListView
from .models import Product

class IndexView(ListView):
    model = Product
    template_name = 'digitalmarket/index.html'
    

class ProductDetailView(DetailView):
    model = Product

    # def get_queryset(self):
    #     pk = self.kwargs['pk']
    #     return Product.objects.filter(pk=pk)
