import json
from .models import *
from store.models import Product

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    print('cart:' , cart)
    items =[]
    order = {
        'total_order_total':0 , 'total_order_items':0
    }
    cartItems = order['total_order_items']

    for i in cart:
        try:
            cartItems += cart[i]['quantity']

            menu = Product.objects.get(id=i)
            total = (menu.price * cart[i]['quantity'])

            order['total_order_total'] += total
            order['total_order_items'] += cart[i]['quantity']

            item = {
                'menu': {
                    'id': menu.id,
                    'name':menu.name,
                    'price': menu.price,
                    'imageURL': menu.imageURL,
                    },
                'quantity': cart[i]['quantity'],
                'get_total': total
                }
            items.append(item)
        except:
            pass
    return { 'items': items, 'order': order, 'cartItems':cartItems }

def cartData(request):
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(
            name= request.user.username,
            phone_number = '25474899087'
        )
        #customa = customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items= order.orderitem_set.all()
        cartItems = order.total_order_items
        print('cartdata')

    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        items = cookieData['items']
        order = cookieData['order']
    return{ 'items': items, 'order': order, 'cartItems':cartItems }


def guestOrder(request , data):
    print('user is not logged in')

    print('COOKIES:', request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer = Customer.objects.create(
        email=email,
        name =name,
    )
    

    order = Order.objects.create(
        customer=customer,
        complete=False
    )

    for item in items:
        menu = Product.objects.get(id=item['menu']['id'])

        orderItem = OrderItem.objects.create(
            menu=menu,
            order = order,
            quantity = item['quantity']
        )
    return customer , order

        