from django.contrib import admin
from.models import product_cloth,product_jwellary

# Register your models here.
class product_clothadmin(admin.ModelAdmin):
    list_display=['id','name','price','cat','pdetails',]
    list_filter=['cat','price',]
    
class product_jewllaryadmin(admin.ModelAdmin):
    list_display=['id','name','price','cat','pdetails',]
    list_filter=['cat','price',]

    

admin.site.register(product_cloth,product_clothadmin)
admin.site.register(product_jwellary,product_jewllaryadmin)

