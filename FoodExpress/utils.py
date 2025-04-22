from flask import session
from models import MenuItem

def get_cart_items():
    """Get the items in the cart with their details"""
    if 'cart' not in session:
        return []
    
    cart_items = []
    for item_id, quantity in session['cart'].items():
        menu_item = MenuItem.query.get(int(item_id))
        if menu_item:
            cart_items.append({
                'id': menu_item.id,
                'name': menu_item.name,
                'price': menu_item.price,
                'image_url': menu_item.image_url,
                'quantity': quantity,
                'subtotal': menu_item.price * quantity,
                'restaurant_name': menu_item.restaurant.name,
                'restaurant_id': menu_item.restaurant.id
            })
    
    return cart_items

def get_cart_total():
    """Calculate the total price of items in the cart"""
    cart_items = get_cart_items()
    return sum(item['subtotal'] for item in cart_items)
