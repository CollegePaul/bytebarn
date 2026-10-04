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