from django.urls import path
from ecomm11_app import views
from ecomm11 import settings
from django.conf.urls.static import static



urlpatterns = [
    path('',views.home,name='index'),
    path('pcdetails/<pcid>/', views.product_c,name='pcdetails'),
    path('pjdetails/<pjid>',views.product_j,name='pjdetails'),
    path('register', views.register, name='register'),
    path('login',views.user_login),
    path('logout',views.user_logout),
    path('catfilter/<cv>',views.catfilter),
    path('range',views.range),
    path('viewcart/', views.view_cart, name='viewcart'),
    path('add-to-cart/<str:product_type>/<int:pid>', views.add_to_cart, name='add_to_cart'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-success/<str:order_id>/', views.order_success, name='order_success'),
    path('makepayment/<str:order_id>/',views.makepayment,name='makepayment'),
    path('address/<str:order_id>/', views.address, name='address'),
    path('sendusermail/<str:order_id>/',views.sendusermail),

    

]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)