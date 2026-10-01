from django.conf import settings
from decimal import Decimal

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID, {})
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product_id, name, price, quantity=1):
        product_id = str(product_id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'id': product_id,
                'name': name,
                'price': str(price),
                'quantity': quantity
            }
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def update_quantity(self, product_id, quantity):
        product_id = str(product_id)
        if product_id in self.cart:
            if quantity <= 0:
                self.remove(product_id)
            else:
                self.cart[product_id]['quantity'] = quantity
            self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        cart = self.cart.copy()
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.save()