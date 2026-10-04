# 11 — The basket

**Mission:** let visitors add products, change quantities, remove things and see a running total — all without a Basket table in the database.
**Time:** about 50 minutes
**You will have when you finish:** a working basket, with a badge in the navbar showing how many things are in it.

---

## Before you start

- Guide 10 is finished and committed
- `shop/cart.py` exists with `get_cart` and `cart_count` (from Guide 07)

---

## The big idea: the basket lives in the session

A basket needs to remember *"you, that anonymous visitor, wanted two of this
thing"* between page loads. There are two ways to do that:

| Way | What it means |
|-----|---------------|
| A `Basket` table in the database | more code, more tables, more migrations |
| The **session** | a dictionary Django stores for us |

We use the session. It is a `{product_id: quantity}` dictionary that Django saves
in a cookie, and hands back to us on every page load.

```
    request.session["cart"] = {"3": 2, "7": 1}
                                 │   │  └─ quantity
                                 │   └──── product 7
                                 └──────── 2 of product 3
```

> **Sessions are not signed in.** A logged-out visitor still gets a basket, and
> it survives them logging in. That is what we want.

---

## Step 1 — Fill in `shop/cart.py`

Replace the stub from Guide 07 with the whole thing:

```python
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
```

### Four things worth understanding

**`request.session.modified = True`** — Django only re-sends the session cookie
if it thinks the session changed. Without this line, add-to-basket silently does
nothing and you lose an afternoon.

**`str(product.pk)`** — session keys end up as JSON, and JSON only allows *string*
keys. So the dictionary looks like `{"3": 2}` not `{3: 2}`. This trips everybody
once.

**`cart.get(key, 0) + quantity`** — adding something already in the basket
increases the count instead of creating a second row. That is the behaviour of a
real shop.

**`Product.objects.filter(pk__in=[...])`** — one query for all the products,
even if there are twenty in the basket. The naive version — a `Product.objects.get()`
inside the loop — makes twenty queries. Watch the query count in
`python manage.py shell` if you are curious. This is the single most useful
performance habit in Django.

---

## Step 2 — Four views

Add to `shop/views.py`:

```python
from django.views.decorators.http import require_POST

from . import cart


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
```

### Why `@require_POST`?

Adding to a basket **changes data**, so it must not be a GET request. A GET is
the thing people get by clicking a link, and links get prefetched by browsers
and crawled by search engines. If adding to the basket were a GET, a browser
could empty your basket by prefetching links.

`@require_POST` turns any GET into a friendly 405 "Method Not Allowed" instead of
doing the damage. Three words, no security review needed.

### Why `redirect` and not `render`?

After a POST the data is saved, so the browser's address bar is still pointing at
the old page. If you `render` it, then pressing F5 asks the server to send that
POST again — so it adds twice. `redirect` sends a "now go here" instruction, and
the refresh becomes a harmless GET.

**This is called the Post/Redirect/Get pattern.** Use it after every POST.

---

## Step 3 — The URLs

In `shop/urls.py`:

```python
urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.product_list, name="product_list"),
    path("shop/<slug:slug>/", views.product_detail, name="product_detail"),
    path("basket/", views.cart_view, name="cart"),
    path("basket/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("basket/update/", views.cart_update, name="cart_update"),
    path("basket/remove/<int:pk>/", views.cart_remove, name="cart_remove"),
]
```

**Checkpoint.** <http://127.0.0.1:8000/basket/> works. Your navbar Basket link
stops 404ing.

---

## Step 4 — Wire up the buttons

In `_product_card.html`, turn the dead button into a real form:

```html
    <form action="{% url 'shop:cart_add' product.pk %}" method="post" class="mt-auto">
      {% csrf_token %}
      <button class="btn btn-primary btn-sm w-100" type="submit">Add to basket</button>
    </form>
```

And in `product_detail.html`, point the form at the same view:

```html
    <form action="{% url 'shop:cart_add' product.pk %}" method="post" class="d-flex gap-2">
      {% csrf_token %}
      <input type="number" name="qty" value="1" min="1" class="form-control" style="max-width: 6rem">
      <button class="btn btn-primary flex-grow-1" type="submit">Add to basket</button>
    </form>
```

**Checkpoint.** Click *Add to basket*. You are taken to `/basket/` and a green
message says what you added.

---

## Step 5 — The badge in the navbar

In `base.html`, change the Basket link to:

```html
          <li class="nav-item">
            <a class="nav-link" href="{% url 'shop:cart' %}">
              Basket
              {% if cart_count %}<span class="badge text-bg-warning">{{ cart_count }}</span>{% endif %}
            </a>
          </li>
```

`cart_count` comes from the context processor you set up in Guide 07, so it works
on every page without any view passing it.

**Checkpoint.** A small yellow number next to *Basket*.

---

## Step 6 — The basket page

Create `templates/shop/cart.html`:

```html
{% extends "base.html" %}
{% load static %}

{% block title %}Your basket — ByteBarn{% endblock %}

{% block content %}
<h1 class="page-title">Your basket</h1>

{% if items %}
  <div class="row g-4">
    <div class="col-lg-8">
      <!-- One form wrapping the whole table, so "Update basket" saves them all -->
      <form action="{% url 'shop:cart_update' %}" method="post">
        {% csrf_token %}

        <div class="card border-0 shadow-sm">
          <div class="table-responsive">
            <table class="table align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th scope="col">Product</th>
                  <th scope="col" class="text-end">Price</th>
                  <th scope="col" style="width: 8rem;">Quantity</th>
                  <th scope="col" class="text-end">Line total</th>
                  <th scope="col"></th>
                </tr>
              </thead>
              <tbody>
                {% for item in items %}
                  <tr>
                    <td>
                      <div class="d-flex align-items-center gap-3">
                        <img src="{% static 'img/' %}{{ item.product.image }}"
                             alt="{{ item.product.name }}" width="72" class="rounded">
                        <div>
                          <a href="{{ item.product.get_absolute_url }}"
                             class="text-decoration-none text-body fw-semibold">
                            {{ item.product.name }}
                          </a>
                          <div class="small text-body-secondary">{{ item.product.get_category_display }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="text-end">{{ currency }}{{ item.product.price }}</td>
                    <td>
                      <!-- The field name tells cart_update which line this is -->
                      <input type="number" class="form-control form-control-sm"
                             name="quantity_{{ item.product.pk }}"
                             value="{{ item.quantity }}" min="0" max="99">
                    </td>
                    <td class="text-end fw-semibold">{{ currency }}{{ item.line_total }}</td>
                    <td class="text-end">
                      <button class="btn btn-sm btn-outline-danger"
                              formaction="{% url 'shop:cart_remove' item.product.pk %}"
                              formmethod="post" type="submit">Remove</button>
                    </td>
                  </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
        </div>

        <div class="d-flex gap-2 mt-3">
          <button type="submit" class="btn btn-outline-primary">Update basket</button>
          <a href="{% url 'shop:product_list' %}" class="btn btn-outline-secondary">Keep shopping</a>
        </div>
      </form>
    </div>

    <!-- ============ Summary ============ -->
    <div class="col-lg-4">
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <h2 class="h5 mb-3">Order summary</h2>
          <div class="d-flex justify-content-between mb-2">
            <span>Items</span>
            <span>{{ cart_count }}</span>
          </div>
          <hr>
          <div class="d-flex justify-content-between fs-5 fw-bold">
            <span>Total</span>
            <span>{{ currency }}{{ total }}</span>
          </div>

          {% if user.is_authenticated %}
            <a href="#" class="btn btn-success w-100 mt-3">Place order</a>
          {% else %}
            <a href="{% url 'login' %}?next={{ request.path }}"
               class="btn btn-success w-100 mt-3">Log in to check out</a>
            <p class="small text-body-secondary text-center mt-2 mb-0">
              No account yet? <a href="{% url 'accounts:register' %}">Register</a>
            </p>
          {% endif %}

          <p class="small text-body-secondary mt-3 mb-0">
            This is a practice shop. No money changes hands.
          </p>
        </div>
      </div>
    </div>
  </div>
{% else %}
  <div class="empty-state p-5 text-center">
    <h2 class="h4">Your basket is empty</h2>
    <p class="text-body-secondary">Nothing in here yet.</p>
    <a href="{% url 'shop:product_list' %}" class="btn btn-primary">Go to the shop</a>
  </div>
{% endif %}
{% endblock %}
```

### Four things to understand

**`name="quantity_{{ item.product.pk }}"`** — the input's name is built from the
product id, so it arrives as `quantity_3`, `quantity_7`. The view loops over
whatever came in and strips the prefix. That is how one form updates five lines
without any JavaScript.

**`{% if items %}`** — if the basket is empty you get a friendly message, not an
empty table with a £0.00 total floating in it.

**`formaction` and `formmethod` on the Remove button** — the Remove button lives
inside the big update form, but it posts somewhere else. HTML lets any button
override where its form submits to.

**`{% url 'login' %}?next={{ request.path }}`** — send a logged-out visitor to
login and remember where they were. `request.path` is the current path. After
logging in they come straight back to their basket.

---

## Step 7 — Check it works

1. Add a product from the shop page. Green message, badge shows `1`.
2. Add the same product again. Badge shows `2`.
3. Open the basket. Change the quantity to `5`, press **Update basket**. The
   line total updates.
4. Set a quantity to `0` and press **Update basket**. The line disappears.
5. Press **Remove**. The line disappears immediately.
6. Log out, add something, and check the basket is still there when you log back
   in.
7. Click **Log in to check out** while logged out — you go to the login page and
   back to the basket afterwards.

**All seven should work.** If one does not, check the list below before moving on.

---

## Mission complete

- [ ] The basket lives in the session, not in a database table
- [ ] Adding the same product twice increases the quantity
- [ ] The badge shows the number of things in the basket
- [ ] Quantities can be changed and a quantity of 0 removes the line
- [ ] Remove deletes the line
- [ ] An empty basket shows a helpful message
- [ ] Every write view has `@require_POST` and ends in a `redirect`
- [ ] The basket survives logging out and back in

**Commit:** `git commit -m "Guide 11: shopping basket"`

---

## If something goes wrong

**Clicking Add to basket does nothing**
Missing `{% csrf_token %}`, or the form has no `method="post"`.

**`DisallowedHost` / `Bad Request (400)` on submit**
`{% csrf_token %}` is missing. It must be inside every `<form method="post">`.

**The badge never appears**
Check `{% if cart_count %}` is inside the `<li>`, and that
`shop.context_processors.shop` is in the `context_processors` list in
`settings.py`. Restart the server after editing settings.

**Adding twice creates two rows**
Your `add_to_cart` uses `cart.get(key, 0) + quantity`. If it uses `=` instead of
`+=`, the second add replaces the first.

**`KeyError: 3` in the view**
You used `int(product.pk)` as the key in one place and `str(product.pk)` in
another. **Keys are always strings.**

**`TypeError: 'int' object is not iterable` in `cart_details`**
`cart` is not a dictionary — usually you assigned `get_cart(request)` the wrong
way round.

**Clicking Remove updates every quantity instead**
The Remove button is missing its `formaction`. It must point at
`shop:cart_remove`.

**`The current path didn't match any URL`**
`request.path` is empty, or you used `{% url request.path %}` instead of
`{{ request.path }}`. Note the two kinds of braces.

**Adding to the basket with a GET (e.g. by typing the URL) returns 405**
Correct. That is `@require_POST` doing its job. It is meant to.

---

Next: [12 — Checkout and purchase history](12-orders-and-history.md)