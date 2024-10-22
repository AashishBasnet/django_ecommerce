from .cart import Cart

#create context processor so our cart workks on all pages

def cart (request):
    return{
        'cart':Cart(request)
    }