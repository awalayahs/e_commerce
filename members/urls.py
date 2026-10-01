from django.urls import path
from members import views

urlpatterns = [
    path('', views.members, name='members'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('members_list/', views.members_list, name='members_list'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('products/', views.products, name='products'),

    # Authentication
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),

    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.success, name='success'),
]
