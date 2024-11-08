
from Home.models import Product, Profile
from decimal import Decimal


class Cart():
    def __init__(self, request):
        self.session = request.session
        # get request
        self.request = request
        # Get the current session key if it exists
        cart = self.session.get('session_key')

        # if user is new i.e no session key
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # Make sure cart is available on all pages of site
        self.cart = cart

    def db_add(self, product, quantity):
        product_id = str(product)
        product_qty = str(quantity)

        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.product_price)}
            self.cart[product_id] = int(product_qty)
        self.session.modified = True
        # deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.filter(
                user__id=self.request.user.id)
            # Convert {'3':1,'2':4} to {"3":1,"2":4}
            cart_converter = str(self.cart)
            cart_converter = cart_converter.replace("\'", "\"")
            # save cart_converter to profile model
            current_user.update(old_cart=str(cart_converter))

    def add(self, product, quantity):
        product_id = str(product.id)
        product_qty = str(quantity)

        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.product_price)}
            self.cart[product_id] = int(product_qty)
        self.session.modified = True
        # deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.filter(
                user__id=self.request.user.id)
            # Convert {'3':1,'2':4} to {"3":1,"2":4}
            cart_converter = str(self.cart)
            cart_converter = cart_converter.replace("\'", "\"")
            # save cart_converter to profile model
            current_user.update(old_cart=str(cart_converter))

    def cart_total(self):
        # Get Product IDs
        product_ids = self.cart.keys()
        # lookup these keys in your product database model
        products = Product.objects.filter(id__in=product_ids)
        quantities = self.cart
        # start counting at 0
        total = 0
        vat_total = 0
        vat = 0
        # vat
        vat_rate = Decimal('0.13')
        for key, value in quantities.items():
            # convert key string into int so we can do math
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.product_sale_price is not None:
                        total = total + (product.product_sale_price * value)
                        vat = total * vat_rate
                        vat_total = total + vat
                        vat_total = round(vat_total, 2)

                    else:
                        total = total + (product.product_price * value)
                        vat = total * vat_rate
                        vat_total = total + vat
                        vat_total = round(vat_total, 2)
        return vat_total

    def cart_sub_total(self):
        # Get Product IDs
        product_ids = self.cart.keys()
        # lookup these keys in your product database model
        products = Product.objects.filter(id__in=product_ids)
        quantities = self.cart
        # start counting at 0
        sub_total = 0
        for key, value in quantities.items():
            # convert key string into int so we can do math
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.product_sale_price is not None:
                        sub_total = sub_total + \
                            (product.product_sale_price * value)
                    else:
                        sub_total = sub_total + (product.product_price * value)
        return sub_total

    def __len__(self):
        return len(self.cart)

    def get_prods(self):
        # get ids from cart
        product_ids = self.cart.keys()
        # use ids to look up products in database model
        products = Product.objects.filter(id__in=product_ids)
        # return looked up products
        return products

    def get_quants(self):
        quantities = self.cart
        return quantities

    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)
        # Get Cart
        outcart = self.cart
        # Update Dictionary/Cart
        outcart[product_id] = product_qty

        self.session.modified = True

        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.filter(
                user__id=self.request.user.id)
            # Convert {'3':1,'2':4} to {"3":1,"2":4}
            cart_converter = str(self.cart)
            cart_converter = cart_converter.replace("\'", "\"")
            # save cart_converter to profile model
            current_user.update(old_cart=str(cart_converter))

        thing = self.cart
        return thing

    def delete(self, product):
        product_id = str(product)
        # Delete From Dictionary/Cart

        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified = True

        # deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.filter(
                user__id=self.request.user.id)
            # Convert {'3':1,'2':4} to {"3":1,"2":4}
            cart_converter = str(self.cart)
            cart_converter = cart_converter.replace("\'", "\"")
            # save cart_converter to profile model
            current_user.update(old_cart=str(cart_converter))
