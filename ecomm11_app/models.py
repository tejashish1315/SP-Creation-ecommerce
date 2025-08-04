from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class product_cloth(models.Model):
    CAT1=((1,'MENS_WEAR'),(2,'WOMEN_WEAR'),(3,'KIDS_WEAR'),)
    name=models.CharField(max_length=50,verbose_name="product name")
    price=models.FloatField()
    pdetails=models.CharField(max_length=200,verbose_name="product details")
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.IntegerField(default=0)
    cat=models.IntegerField(choices=CAT1,verbose_name="category")
    is_active=models.BooleanField(default=True,verbose_name="Available")
    pimage=models.ImageField(upload_to="image")
    
class product_jwellary(models.Model):
    CAT2=((4,'MENS_JWELLARY'),(5,'WOMEN_JWELLARY'),(6,'KIDS_JWELLARY'))
    name=models.CharField(max_length=50,verbose_name="product name")
    price=models.FloatField()
    pdetails=models.CharField(max_length=200,verbose_name="product details")
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.IntegerField(default=0)
    cat=models.IntegerField(choices=CAT2,verbose_name="category")
    is_active=models.BooleanField(default=True,verbose_name="Available")
    pimage=models.ImageField(upload_to="image")


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cloth_product = models.ForeignKey(product_cloth, null=True, blank=True, on_delete=models.CASCADE)
    jwellary_product = models.ForeignKey(product_jwellary, null=True, blank=True, on_delete=models.CASCADE)
    product_type = models.CharField(max_length=50, default='product_cloth')  # e.g. 'cloth' or 'jwellary'
    quantity = models.PositiveIntegerField(default=1)
    added_on = models.DateTimeField(auto_now_add=True)

    def get_product(self):  # ✅ properly indented inside the class
        if self.product_type == 'cloth':
            return self.cloth_product
        elif self.product_type == 'jwellary':
            return self.jwellary_product
        return None

    def get_price(self):
        product = self.get_product()
        return product.offer_price if product and product.offer_price else product.price if product else 0

    def get_subtotal(self):
        return self.get_price() * self.quantity

    def get_you_save(self):
        product = self.get_product()
        if product and product.offer_price:
            return (product.price - product.offer_price) * self.quantity
        return 0
class Order(models.Model):
    order_id = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cloth_product = models.ForeignKey(product_cloth, null=True, blank=True, on_delete=models.CASCADE)
    jwellary_product = models.ForeignKey(product_jwellary, null=True, blank=True, on_delete=models.CASCADE)
    product_type = models.CharField(max_length=50, default='cloth')
    qty = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0) 
    status = models.CharField(max_length=20, default="Pending")  # e.g. Pending, Paid, Delivered

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.line1}, {self.city}, {self.state}"
