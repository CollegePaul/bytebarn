from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import cart
from .models import Order, OrderItem, Product

# The slots in the PC Builder, in the order they appear on the page.
# Each value is a Product category.
BUILDER_SLOTS = ["cpu", "gpu", "ram", "storage", "cooling", "case", "psu"]


# --- Pages anybody can see ----------------------------------------------------


def home(request):
    """The landing page. Shows a handful of featured products."""
    products = Product.objects.filter(featured=True, stock__gt=0)
    return render(request, "shop/home.html", {"products": products})


def product_list(request):
    """The shop window: every product, with filters that work without JavaScript."""
    products = Product.objects.filter(stock__gt=0)

    # These come from the query string, e.g. /shop/?category=gpu&q=radeon
    selected_category = request.GET.get("category", "")
    query = request.GET.get("q", "").strip()

    if selected_category:
        products = products.filter(category=selected_category)
    if query:
        products = products.filter(name__icontains=query)

    context = {
        "products": products,
        "categories": Product.CATEGORY_CHOICES,
        "selected_category": selected_category,
        "query": query,
    }
    return render(request, "shop/product_list.html", context)


def product_detail(request, slug):
    """One product on its own page."""
    product = get_object_or_404(Product, slug=slug)
    return render(request, "shop/product_detail.html", {"product": product})


def builder(request):
    """The PC cost calculator.

    The prices come from the database, so the calculator can never disagree with
    the shop. All of the adding-up happens in JavaScript in the browser.
    """
    products = Product.objects.filter(stock__gt=0)

    # Turn the flat list of products into one group per builder slot, skipping
    # any category we have no products for.
    labels = dict(Product.CATEGORY_CHOICES)
    groups = [
        {
            "value": slot,
            "label": labels[slot],
            "parts": [p for p in products if p.category == slot],
        }
        for slot in BUILDER_SLOTS
    ]
    groups = [group for group in groups if group["parts"]]

    return render(request, "shop/builder.html", {"groups": groups})


@require_POST
def builder_add_to_cart(request):
    """Put every part chosen in the builder into the basket in one go."""
    added = 0

    for slot in BUILDER_SLOTS:
        product_id = request.POST.get(slot)
        if not product_id:
            continue

        # We check the category too, otherwise someone could hand-post a
        # different product id in the cpu slot and get it for free.
        product = Product.objects.filter(
            pk=product_id, category=slot, stock__gt=0
        ).first()

        if product:
            cart.add_to_cart(request, product)
            added += 1

    if added:
        messages.success(request, f"Added {added} part(s) to your basket.")
    else:
        messages.warning(request, "Pick at least one part first.")

    return redirect("shop:cart")


# --- Basket -------------------------------------------------------------------


def cart_view(request):
    items, total = cart.cart_details(request)
    return render(request, "shop/cart.html", {"items": items, "total": total})


@require_POST
def cart_add(request, pk):
    """Add a product to the basket. The product page can ask for a quantity."""
    product = get_object_or_404(Product, pk=pk)

    try:
        quantity = max(1, int(request.POST.get("qty", 1)))
    except (TypeError, ValueError):
        quantity = 1

    cart.add_to_cart(request, product, quantity)
    messages.success(request, f'Added "{product.name}" to your basket.')
    return redirect("shop:cart")


@require_POST
def cart_update(request):
    """Change every quantity on the basket page at once.

    The form sends fields called quantity_3, quantity_7 and so on. We loop over
    whatever arrived and update each line.
    """
    for key, value in request.POST.items():
        if not key.startswith("quantity_"):
            continue

        product_id = int(key.replace("quantity_", ""))

        try:
            quantity = int(value)
        except (TypeError, ValueError):
            quantity = 0

        cart.set_quantity(request, product_id, quantity)

    messages.success(request, "Basket updated.")
    return redirect("shop:cart")


@require_POST
def cart_remove(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart.remove_from_cart(request, product.pk)
    messages.info(request, f'Removed "{product.name}".')
    return redirect("shop:cart")


@login_required
@require_POST
def checkout(request):
    """Turn the basket into a real order in the database."""
    items, total = cart.cart_details(request)

    if not items:
        messages.warning(request, "Your basket is empty.")
        return redirect("shop:cart")

    # transaction.atomic means: if anything below goes wrong, nothing is saved.
    # Either we get a whole order or we get nothing at all.
    with transaction.atomic():
        order = Order.objects.create(
            customer=request.user, total=total, status="paid"
        )

        for item in items:
            product = item["product"]
            quantity = item["quantity"]

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,  # copy the price, so it never changes later
            )

            # Take the stock away.
            # Mission: if two people buy the last one at the same moment, this
            # can go negative. Look up F() expressions and fix it.
            product.stock -= quantity
            product.save(update_fields=["stock"])

    cart.clear_cart(request)
    messages.success(request, f"Order #{order.pk} placed. Thank you!")
    return redirect("shop:order_detail", order_id=order.pk)


@login_required
def order_detail(request, order_id):
    """A receipt for one order.

    Notice `customer=request.user` in the lookup. Without it, a customer could
    type another order number into the address bar and read someone else's
    receipt.
    """
    order = get_object_or_404(Order, pk=order_id, customer=request.user)
    return render(request, "shop/order_detail.html", {"order": order})