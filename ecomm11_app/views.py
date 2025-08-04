from django.shortcuts import render, HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.views import View
from .models import product_cloth, product_jwellary,Cart,Order
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
import razorpay
from django.core.mail import send_mail
import uuid
from django.utils.timezone import now







# Create your views here.
def home(request):
    # print(request.user.id)
    # print(request.user.is_authenticated)
    p1 = product_cloth.objects.filter(is_active=True)
    p2 = product_jwellary.objects.filter(is_active=True)

    context = {
        'product_cloths': p1,
        'product_jwellarys': p2
    }
    return render(request,'index.html',context)

def product_c(request, pcid):
    p1 = get_object_or_404(product_cloth, is_active=True, id=pcid)
    related_products = product_cloth.objects.filter(cat=p1.cat, is_active=True).exclude(id=pcid)[:4]

    context = {
        'product_cloth': p1,  
        'related_products': related_products,  # list of related products
    }
    return render(request, 'product_cloth.html', context)

def product_j(request,pjid):
    p2 = get_object_or_404(product_jwellary, is_active=True, id=pjid)
    related_products = product_jwellary.objects.filter(cat=p2.cat, is_active=True).exclude(id=pjid)[:4]


    context={}
    context = {
            'product_jwellarys': p2,
            'related_product':related_products,
        }
    return render(request,'product_jwellary.html',context)

def register(request):
    if request.method=='POST':
        uname=request.POST['uname']
        umail=request.POST['umail']
        upass=request.POST['upass']
        ucpass=request.POST['ucpass']
        context={}
        if uname=="" or umail=="" or upass=="" or ucpass=="":
            context['errmsg']="Fields cannot be Empty"
        elif upass!=ucpass:
            context['errmsg']="password and confirm password should be same."    
             
        else:
            try:    
                u=User.objects.create(password=upass,username=uname,email=umail)
                u.set_password(upass)
                u.save()
                context['success']="User register successfully ,please login"
            except Exception:
                context['errmsg']="User already exists."    
        return render(request,"register.html",context)
        
    else:
        return render(request, 'register.html')
    
def user_login(request):
    if request.method=="POST":
        uname=request.POST['uname']
        umail=request.POST['umail']
        upass=request.POST['upass']
        context={}
        if uname=="" or umail=="" or upass=="":
            context['errmsg']="Fields cannot be Empty."    
            return render(request,"login.html",context)
        else:
            u=authenticate(username=uname,useremail=umail,password=upass)
            if u is not None:
                login(request,u)
                return redirect('/')
            else:
                context['errmsg']="Username and password is invalid."    
                return render(request,"login.html",context)
            
    else:
        return render(request,'login.html')
    
def user_logout(request):
    logout(request)
    return redirect('/') 

def catfilter(request, cv):
    category = ['cloth', 'jwellary']
    
    q1 = Q(is_active=True)
    q2 = Q(cat=cv)

    p1 = product_cloth.objects.filter(q1 & q2)
    p2 = product_jwellary.objects.filter(q1 & q2)

    context = {
        'product_cloths': p1,
        'product_jwellarys': p2,
    }
    return render(request, 'index.html', context)

def range(request):
    # Safely convert GET parameters to integers/floats
    try:
        min_price = float(request.GET.get('min', 0))
        max_price = float(request.GET.get('max', 0))
    except ValueError:
        min_price, max_price = 0, 0  # Default to zero or handle error

    # Build one combined Q object
    price_filter = Q(price__gte=min_price) & Q(price__lte=max_price) & Q(is_active=True)

    # Apply same filter to both models
    product_cloths = product_cloth.objects.filter(price_filter)
    product_jewellery = product_jwellary.objects.filter(price_filter)

    return render(request, 'index.html', {
        'product_cloths': product_cloths,
        'product_jewellery': product_jewellery,
    })

def about(request):
    return render(request, 'about.html')


def add_to_cart(request, product_type, pid):
    if not request.user.is_authenticated:
        messages.info(request, "Please login before adding items to your cart.")
        return render(request,'login.html')  # Redirect to login if user not authenticated

    # Handle product retrieval based on type
    if product_type == 'cloth':
        product = get_object_or_404(product_cloth, id=pid)
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            cloth_product=product,
            product_type='cloth'
        )
    elif product_type == 'jwellary':
        product = get_object_or_404(product_jwellary, id=pid)
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            jwellary_product=product,
            product_type='jwellary'
        )
    else:
        messages.error(request, "Invalid product type.")
        return redirect('index')

    # Update quantity if already in cart
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.info(request, 'Product already in cart. Quantity increased.')
    else:
        messages.success(request, 'Product added to cart successfully!')

    # ✅ Redirect to the cart page or homepage after adding to cart
    return redirect('viewcart')  # or use 'index'


def view_cart(request):
    if not request.user.is_authenticated:
        return redirect('login')

    cart_items = Cart.objects.filter(user=request.user)
    total = 0

    for item in cart_items:
        item.product = item.get_product()
        item.price = item.get_price()
        item.subtotal = item.get_subtotal()
        item.you_save = item.get_you_save()
        total += item.subtotal

    return render(request, 'viewcart.html', {
        'cart_items': cart_items,
        'total': total
    })

def contact(request):
    return render(request, 'contact.html')

def update_cart_quantity(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1
        cart_item.save()

    return redirect('viewcart')  # make sure 'view_cart' is your URL name for the cart page

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('viewcart')


def clear_cart(request):
    Cart.objects.filter(user=request.user).delete()
    return redirect('viewcart')



def place_order(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('viewcart')

    order_id = str(uuid.uuid4().hex[:10]).upper()

    for item in cart_items:
        Order.objects.create(
            order_id=order_id,
            user=request.user,
            cloth_product=item.cloth_product,
            jwellary_product=item.jwellary_product,
            product_type=item.product_type,
            qty=item.quantity,
            total_amount=item.get_subtotal(),
            created_at=now(),
            status='Pending'
        )

    cart_items.delete()

    # ✅ Redirect to success page with order_id
    return redirect('order_success', order_id=order_id)

def order_success(request, order_id):
    username = request.user.username if request.user.is_authenticated else "Customer"
    has_address = bool(request.session.get(f'order_{order_id}_address'))

    context = {
        'order_id': order_id,
        'username': username,
        'has_address': has_address,
    }
    return render(request, 'place_order.html', context)

def order_confirmation(request, order_id):
    username = request.user.username if request.user.is_authenticated else "Customer"
    context = {
        'username': username,
        'order_id': order_id,
    }
    return render(request, 'order_confirmation.html', context)


def makepayment(request, order_id):
    orders = Order.objects.filter(order_id=order_id, user=request.user)

    if not orders.exists():
        return redirect('viewcart')  # Redirect if no matching order

    total_amount = sum(o.total_amount for o in orders)

    client = razorpay.Client(auth=("rzp_test_pjmfONoAV5hhRJ", "2qLFlWxOv0vaA1jxWEEHwbcA"))

    payment_order = client.order.create({
        "amount": int(total_amount * 100),
        "currency": "INR",
        "receipt": order_id,
        "payment_capture": 1
    })

    context = {
        "payment": payment_order,
        "order_id": order_id,
        "razorpay_order_id": payment_order['id'],
        "razorpay_key": "rzp_test_pjmfONoAV5hhRJ",  # ✅ Add this
        "amount": int(total_amount * 100),  # ✅ Add this
        'address': address,
        "user_name": request.user.get_full_name() or request.user.username,
        "user_email": request.user.email,
        "user_contact": "",  # Optional

        
    }

    return render(request, 'pay.html', context)


def sendusermail(request, order_id):
    uemail = request.user.email
    msg = f"Order details are: {order_id}\nThank you for purchasing from SP CREATION."

    send_mail(
        subject="Ekart - Order Placed Successfully",
        message=msg,
        from_email="tejashree15b@gmail.com",
        recipient_list=[uemail],
        fail_silently=False,
    )

    user = request.user
    context = {
        'username': user.username,
        'user_id': user.id,
        'order_id': order_id,
    }
    return render(request, 'order_confirmation.html', context)

def address(request, order_id):
    if request.method == 'POST':
        # Retrieve data from the POST request
        line1 = request.POST.get('line1')
        line2 = request.POST.get('line2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')

        # Validate the data (basic example)
        if not line1 or not city or not state or not postal_code or not country:
            messages.error(request, "All fields are required.")
            return render(request, 'address.html')

        # Store the address in the session
        address = {
            'line1': line1,
            'line2': line2,
            'city': city,
            'state': state,
            'postal_code': postal_code,
            'country': country
        }
        request.session[f'order_{order_id}_address'] = address

        return redirect('makepayment', order_id=order_id)

    return render(request, 'address.html')
