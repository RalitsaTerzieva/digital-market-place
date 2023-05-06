from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    seller = models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    price = models.FloatField()
    file = models.FileField(upload_to='uploads')
    
    def __str__(self):
        return self.name
    
    
class OrderDetail(models.Model):
    customer_email = models.EmailField()
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    amount = models.IntegerField()
    stripe_payment_intent = models.CharField(max_length=200)
    has_paid = models.BooleanField(default=False)
    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.product.name
    
