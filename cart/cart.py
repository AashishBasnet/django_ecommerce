
from Home.models import Product


class Cart():
    def __init__(self, request):
        self.session = request.session

        # Get the current session key if it exists
        cart = self.session.get('session_key')

        # if user is new i.e no session key
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # Make sure cart is avialable on all pages of site
        self.cart = cart

    def add(self, product, quantity):
        product_id = str(product.id)
        product_qty = str(quantity)

        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.product_price)}
            self.cart[product_id] =  int(product_qty)
        self.session.modified = True

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

        thing = self.cart
        return thing

    def delete(self, product):
        product_id = str(product)
        #Delete From Dictionary/Cart

        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified = True


    

