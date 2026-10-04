# 14 — Tests and the final checklist

**Mission:** write tests that prove the shop works, then run through everything one last time.
**Time:** about 30 minutes
**You will have when you finish:** a finished project, and tests that catch you when you break it.

---

## Before you start

- Guides 01–13 are finished and committed
- The whole site works

---

## Why write tests?

You have been clicking through the site after every change. That catches real
problems, but it is slow and you will forget a corner.

A test is code that does the clicking for you and tells you pass or fail. In
about a minute you can check all 23 behaviours that took you hours to verify by
hand.

**The payoff is not the first run.** It is three weeks from now, when you change
one line and eleven tests fail, and you know instantly what you broke.

---

## Step 1 — How a Django test works

Django gives you a test client — a fake browser:

```python
class ShopPageTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("shop:home"))
        self.assertEqual(response.status_code, 200)
```

Line by line:

| Piece | What it does |
|-------|--------------|
| `class ShopPageTests(TestCase)` | a group of related tests. **Always** end in `TestCase` |
| `self.client` | a fake browser that does not need a real server |
| `self.client.get("/shop/")` | makes a request and gets back a fake response |
| `self.assertEqual(response.status_code, 200)` | if this is not true, the test fails |

`TestCase` gives you two things for free:

1. **A separate empty database for every test.** Whatever you create in a test is
   thrown away afterwards. Your real products are safe.
2. **Automatic cleanup.** No forgetting to delete things.

---

## Step 2 — The tests

Replace `shop/tests.py` with the whole file below. It is 23 tests and it is the
single most useful file in the project.

```python
"""Tests for the shop.

Run them with:

    python manage.py test

A test is just code that checks something works. If you break the shop on
purpose, these should fail. If you break nothing, they should pass.
"""

from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Order, Product


def make_product(slug="test-cpu", name="Test CPU", price="100.00", **extra):
    return Product.objects.create(slug=slug, name=name, price=Decimal(price), **extra)


class ShopPageTests(TestCase):
    """Pages anyone can look at."""

    def setUp(self):
        self.cpu = make_product()

    def test_home_page_loads(self):
        response = self.client.get(reverse("shop:home"))
        self.assertEqual(response.status_code, 200)

    def test_shop_page_lists_products(self):
        response = self.client.get(reverse("shop:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.cpu.name)

    def test_filter_by_category(self):
        gpu = make_product(slug="test-gpu", name="Test GPU", category="gpu")

        response = self.client.get(reverse("shop:product_list"), {"category": "gpu"})

        self.assertContains(response, gpu.name)
        self.assertNotContains(response, self.cpu.name)

    def test_search_by_name(self):
        make_product(slug="radeon-x", name="Radeon X", category="gpu")

        response = self.client.get(reverse("shop:product_list"), {"q": "radeon"})

        self.assertContains(response, "Radeon X")
        self.assertNotContains(response, self.cpu.name)

    def test_product_detail_page(self):
        response = self.client.get(self.cpu.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.cpu.name)

    def test_unknown_product_gives_404(self):
        response = self.client.get(reverse("shop:product_detail", args=["nope"]))
        self.assertEqual(response.status_code, 404)


class BasketTests(TestCase):
    def setUp(self):
        self.cpu = make_product()

    def add_to_basket(self):
        return self.client.post(
            reverse("shop:cart_add", args=[self.cpu.pk]), {"qty": 1}
        )

    def test_adding_shows_the_item_and_a_badge(self):
        self.add_to_basket()

        response = self.client.get(reverse("shop:cart"))
        self.assertContains(response, self.cpu.name)
        # The badge in the navbar carries the count.
        self.assertContains(response, "badge text-bg-warning")

    def test_adding_twice_increases_the_quantity(self):
        self.add_to_basket()
        self.add_to_basket()

        response = self.client.get(reverse("shop:cart"))
        # The quantity box shows 2.
        self.assertContains(response, 'value="2"')

    def test_remove_from_basket(self):
        self.add_to_basket()
        self.client.post(reverse("shop:cart_remove", args=[self.cpu.pk]))
        response = self.client.get(reverse("shop:cart"))
        self.assertContains(response, "Your basket is empty")

    def test_basket_survives_visiting_another_page(self):
        self.add_to_basket()
        self.client.get(reverse("shop:home"))
        response = self.client.get(reverse("shop:cart"))
        self.assertContains(response, self.cpu.name)

    def test_setting_a_quantity_to_zero_removes_the_line(self):
        self.add_to_basket()
        self.client.post(
            reverse("shop:cart_update"), {f"quantity_{self.cpu.pk}": 0}
        )
        response = self.client.get(reverse("shop:cart"))
        self.assertContains(response, "Your basket is empty")


class CheckoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("sam", password="testpassword123")
        self.cpu = make_product(price="100.00")

    def test_checkout_needs_a_login(self):
        self.client.post(reverse("shop:cart_add", args=[self.cpu.pk]))
        response = self.client.post(reverse("shop:checkout"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_checkout_creates_an_order(self):
        self.client.login(username="sam", password="testpassword123")
        self.client.post(reverse("shop:cart_add", args=[self.cpu.pk]))
        self.client.post(reverse("shop:checkout"))

        order = Order.objects.get(customer=self.user)

        self.assertEqual(order.total, Decimal("100.00"))
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.item_count, 1)

    def test_checkout_empties_the_basket(self):
        self.client.login(username="sam", password="testpassword123")
        self.client.post(reverse("shop:cart_add", args=[self.cpu.pk]))
        self.client.post(reverse("shop:checkout"))

        response = self.client.get(reverse("shop:cart"))
        self.assertContains(response, "Your basket is empty")

    def test_checkout_takes_stock_away(self):
        product = make_product(slug="low-stock", name="Low Stock", stock=3)
        self.client.login(username="sam", password="testpassword123")
        self.client.post(reverse("shop:cart_add", args=[product.pk]), {"qty": 2})
        self.client.post(reverse("shop:checkout"))

        product.refresh_from_db()
        self.assertEqual(product.stock, 1)

    def test_cannot_read_someone_elses_order(self):
        other = User.objects.create_user("alex", password="testpassword123")
        their_order = Order.objects.create(customer=other, total=Decimal("10.00"))

        self.client.login(username="sam", password="testpassword123")
        response = self.client.get(reverse("shop:order_detail", args=[their_order.pk]))

        self.assertEqual(response.status_code, 404)

    def test_order_history_only_shows_my_orders(self):
        Order.objects.create(customer=self.user, total=Decimal("10.00"))
        other = User.objects.create_user("alex", password="testpassword123")
        Order.objects.create(customer=other, total=Decimal("99.00"))

        self.client.login(username="sam", password="testpassword123")
        response = self.client.get(reverse("accounts:order_history"))

        self.assertContains(response, "10.00")
        self.assertNotContains(response, "99.00")


class AccountTests(TestCase):
    def test_register_creates_a_user_and_logs_them_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newbie",
                "first_name": "New",
                "email": "new@example.com",
                "password1": "testpassword123",
                "password2": "testpassword123",
            },
        )

        self.assertRedirects(response, reverse("accounts:dashboard"))
        self.assertTrue(User.objects.filter(username="newbie").exists())

    def test_register_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newbie",
                "email": "new@example.com",
                "password1": "testpassword123",
                "password2": "differentpassword123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newbie").exists())

    def test_dashboard_needs_a_login(self):
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertEqual(response.status_code, 302)


class BuilderTests(TestCase):
    def setUp(self):
        self.cpu = make_product(slug="b-cpu", name="Builder CPU", category="cpu")
        self.gpu = make_product(slug="b-gpu", name="Builder GPU", category="gpu")

    def test_builder_page_loads(self):
        response = self.client.get(reverse("shop:builder"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.cpu.name)

    def test_add_build_to_cart(self):
        response = self.client.post(
            reverse("shop:builder_add_to_cart"),
            {"cpu": self.cpu.pk, "gpu": self.gpu.pk},
        )

        self.assertRedirects(response, reverse("shop:cart"))
        cart_page = self.client.get(reverse("shop:cart"))
        self.assertContains(cart_page, self.cpu.name)
        self.assertContains(cart_page, self.gpu.name)

    def test_cannot_smuggle_a_product_into_the_wrong_slot(self):
        # The GPU is posted into the CPU slot. It should be ignored.
        self.client.post(reverse("shop:builder_add_to_cart"), {"cpu": self.gpu.pk})

        cart_page = self.client.get(reverse("shop:cart"))
        self.assertNotContains(cart_page, self.gpu.name)
```

> **`setUp` runs before every test in the class.** It is where you create the
> product or user that test needs. Because each test gets a fresh database, they
> cannot affect each other.

---

## Step 3 — Run them

```bat
python manage.py test
```

**Checkpoint:**

```
Found 23 test(s).
....
.......................................
Ran 23 tests in 1.7s

OK
```

**23 tests. Zero failures. Your shop works.**

To see the detail:

```bat
python manage.py test -v 2
```

---

## Step 4 — Break something on purpose

Tests you have never seen fail are tests you cannot trust. So break something.

In `shop/cart.py`, change `remove_from_cart` to do nothing:

```python
def remove_from_cart(request, product_id):
    pass  # oops
```

Run the tests again:

```
FAIL: test_remove_from_basket (shop.tests.BasketTests)
...
AssertionError: True is not false
```

**The test found your bug in under two seconds.** Put the code back and they all
pass again.

Now try the other direction — remove `customer=request.user` from
`order_detail` in `shop/views.py`. `test_cannot_read_someone_elses_order` will
fail, and that is a **real security bug**, not a typo. That is what tests are
for.

---

## The five most useful assertions

| Assertion | What it checks |
|-----------|----------------|
| `self.assertEqual(response.status_code, 200)` | the page exists |
| `self.assertContains(response, "text")` | the page says what it should |
| `self.assertNotContains(response, "text")` | the page does **not** leak something |
| `self.assertEqual(obj.field, value)` | data was saved correctly |
| `self.assertRedirects(response, "/somewhere/")` | it went where it should |

`assertNotContains` is the one people forget. Use it for anything private — "this
page must not contain another customer's name", "this page must not contain
their email".

---

## The final checklist

Go through this with the site running.

### Does it work?

- [ ] `/` shows four featured product cards
- [ ] `/shop/` lists every product, filters by category, searches by name
- [ ] Clicking a product opens its own page
- [ ] Adding to basket updates the navbar badge
- [ ] The basket lets you change quantities and remove lines
- [ ] An empty basket shows a friendly message
- [ ] Registering logs you in
- [ ] The dashboard shows orders placed, total spent and recent orders
- [ ] Checking out creates an order, empties the basket and reduces stock
- [ ] The receipt shows what was **paid**, not today's price
- [ ] Order history shows only your own orders
- [ ] `/builder/` adds up parts live, checks your budget, and adds to the basket
- [ ] `/admin/` lists products and orders

### Is it tidy?

- [ ] `python manage.py check` — no issues
- [ ] `python manage.py test` — all pass
- [ ] `python manage.py makemigrations --check --dry-run` — no changes pending
- [ ] No dead `#` links left over from earlier guides
- [ ] No `print()` statements in your code
- [ ] Every file you wrote still has the comments explaining it

### Is it ready to hand in?

- [ ] `requirements.txt` is up to date
- [ ] `db.sqlite3` is **not** in git
- [ ] `.venv` is **not** in git
- [ ] Everything is committed
- [ ] `git log --oneline` shows one commit per guide

```bat
git add .
git commit -m "Guide 14: tests and final checklist"
```

---

## Prove it works from scratch

The ultimate test. Delete the database and build it again:

```bat
del db.sqlite3
python manage.py migrate
python manage.py seed_shop
python manage.py createsuperuser
python manage.py runserver
```

If the site comes back, your project is **self-contained**. Anything else — a
missing dependency, a manual database edit, a change you forgot to write down —
shows up immediately.

Add `python manage.py seed_shop` and `python manage.py createsuperuser` to a
short `SETUP.md` so whoever runs this next knows exactly what to type.

---

## What you have learned

You have built, from an empty folder, a working e-commerce site. Along the way:

| Concept | Where |
|---------|-------|
| Models, fields, choices | Guide 05 |
| Migrations | Guide 05 |
| The admin site | Guides 05, 12 |
| Management commands | Guide 06 |
| Views, templates, context | Guides 03, 07 |
| Template inheritance and blocks | Guide 04 |
| Includes and partials | Guide 07 |
| Static files and `{% static %}` | Guides 02, 03 |
| Bootstrap | Guides 03, 07 |
| crispy-forms | Guide 09 |
| Forms, validation, CSRF | Guides 08, 09 |
| Authentication | Guide 09 |
| Decorators and access control | Guides 10, 12 |
| Sessions | Guide 11 |
| Foreign keys and related names | Guides 10, 12 |
| Transactions | Guide 12 |
| JavaScript in the browser | Guide 13 |
| Automated tests | Guide 14 |

**Next steps:** [15 — Stretch missions](15-stretch-missions.md).

---

## If something goes wrong

**`Ran 0 tests`**
The tests are not in a file named `tests.py`, or the classes do not end in
`TestCase`.

**`ImportError: cannot import name 'Order' from 'shop.models'`**
Your model is called something else, or you are mid-guide. The tests assume the
finished project.

**`DisallowedHost: testserver`**
Something called `override_settings` and changed `ALLOWED_HOSTS`. Remove it.

**`NoReverseMatch` in a test**
A URL name is wrong. It runs `reverse()` when the test runs, which is a feature —
it tells you the URL is broken.

**A test passes when it should not**
Usually `assertContains(response, "x")` where `"x"` appears somewhere unrelated
on the page. Use a longer, more specific string.

**Tests are slow**
You have one test that posts to a real URL. Look for `time.sleep` — never put
one in a test.

---

**You have finished the project.** Go and break something on purpose, then fix
it. That is how it really sticks.