"""The shopping basket.

The basket lives in the visitor's session, so there is no Basket model and no
Basket table in the database. A session is just a dictionary that Django stores
for us and hands back on every page load.

The shape of the data is deliberately the simplest thing that works:

    request.session["cart"] = {"3": 2, "7": 1}

which means "give me 2 of product 3, and 1 of product 7".
"""

from decimal import Decimal

from .models import Product

# The name of the key we store the basket under inside the session.
CART_SESSION_KEY = "cart"


def get_cart(request):
    """Return the raw dictionary of {product_id: quantity}."""
    return request.session.get(CART_SESSION_KEY, {})


def save_cart(request, cart):
    """Write the dictionary back into the session."""
    request.session[CART_SESSION_KEY] = cart
    # Tell Django the session changed, otherwise the cookie is not re-sent.
    request.session.modified = True


def add_to_cart(request, product, quantity=1):
    """Add a product to the basket, or top up the quantity if already there."""
    cart = get_cart(request)
    key = str(product.pk)
    cart[key] = cart.get(key, 0) + quantity
    save_cart(request, cart)


def set_quantity(request, product_id, quantity):
    """Set an exact quantity. A quantity of 0 (or less) removes the line."""
    cart = get_cart(request)
    key = str(product_id)

    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = quantity

    save_cart(request, cart)


def remove_from_cart(request, product_id):
    set_quantity(request, product_id, 0)


def clear_cart(request):
    """Empty the basket, e.g. once an order has been placed."""
    request.session.pop(CART_SESSION_KEY, None)
    request.session.modified = True


def cart_details(request):
    """Turn the raw session dictionary into something a template can loop over.

    Returns a tuple of (items, total) where each item is a dictionary with
    "product", "quantity" and "line_total" keys.
    """
    cart = get_cart(request)
    # One query for the whole basket instead of one query per product.
    products = Product.objects.filter(pk__in=[int(key) for key in cart])

    items = []
    total = Decimal("0.00")

    for product in products:
        quantity = cart[str(product.pk)]
        line_total = product.price * quantity
        total += line_total
        items.append(
            {
                "product": product,
                "quantity": quantity,
                "line_total": line_total,
            }
        )

    return items, total


def cart_count(request):
    """Total number of things in the basket. Used for the little badge."""
    return sum(get_cart(request).values())