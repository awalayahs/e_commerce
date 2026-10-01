from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import logout as auth_logout
from .models import Members
from .utils.cart import Cart
import json, os

# -----------------------------
# Public Pages
# -----------------------------
def members(request):
    return render(request, 'index.html')

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def products(request):
    json_path = os.path.join(settings.BASE_DIR, 'members', 'json', 'data.json')
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            categories = data.get('categories', [])
    except:
        categories = []

    cart = Cart(request)
    return render(request, 'products.html', {'categories': categories, 'cart_count': len(cart)})

# -----------------------------
# Authentication
# -----------------------------
def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not all([first_name, last_name, email, password]):
            messages.error(request, "All fields are required.")
            return render(request, 'signup.html')

        if Members.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'signup.html')

        Members.objects.create(first_name=first_name, last_name=last_name, email=email, password=password)
        messages.success(request, "Registration successful!")
        return redirect('login')

    return render(request, 'signup.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not all([email, password]):
            messages.error(request, "Email and password are required.")
            return render(request, 'login.html')

        member = Members.objects.filter(email__iexact=email).first()
        if member and member.password.lower() == password.lower():
            request.session['member_id'] = member.id
            messages.success(request, "Login successful!")
            next_url = request.GET.get('next', 'products')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'login.html')


def logout(request):
    auth_logout(request)
    request.session.flush()
    messages.success(request, "Logged out successfully!")
    return redirect('login')

# -----------------------------
# Require Login Decorator
# -----------------------------
def require_login(view_func):
    def wrapper(request, *args, **kwargs):
        if 'member_id' not in request.session:
            messages.error(request, "Please login first!")
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        return view_func(request, *args, **kwargs)
    return wrapper

# -----------------------------
# Cart Views
# -----------------------------
@require_login
def cart_view(request):
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart, 'cart_count': len(cart)})

@require_login
def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product_name = data.get('product_name')
        product_price = float(data.get('product_price'))
        if not all([product_id, product_name, product_price]):
            return JsonResponse({'status':'error','message':'Missing product info'})
        cart = Cart(request)
        cart.add(product_id, product_name, product_price, 1)
        return JsonResponse({'status':'success','cart_count': len(cart)})
    return JsonResponse({'status':'error','message':'Invalid request method'})

@require_login
def update_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity'))
        cart = Cart(request)
        cart.update_quantity(product_id, quantity)
        return JsonResponse({'status':'success','total_price': str(cart.get_total_price()), 'cart_count': len(cart)})
    return JsonResponse({'status':'error','message':'Invalid request method'})

@require_login
def remove_from_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        cart = Cart(request)
        cart.remove(product_id)
        return JsonResponse({'status':'success','total_price': str(cart.get_total_price()), 'cart_count': len(cart)})
    return JsonResponse({'status':'error','message':'Invalid request method'})

@require_login
def checkout(request):
    cart = Cart(request)
    if not cart.cart:
        messages.error(request, "Your cart is empty")
        return redirect('cart')
    cart.clear()
    messages.success(request, "Thank you for your purchase!")
    return redirect('success')

# -----------------------------
# Dashboard / Members List
# -----------------------------
@require_login
def dashboard(request):
    total_members = Members.objects.count()
    return render(request, 'dashboard.html', {'total_members': total_members})

@require_login
def members_list(request):
    members = Members.objects.all()
    return render(request, 'members_list.html', {'members': members})

def success(request):
    return render(request, 'success.html')
