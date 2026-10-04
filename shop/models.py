from django.conf import settings
from django.db import models
from django.urls import reverse


class Product(models.Model):
    """One thing the shop sells.

    The category is a plain text choice rather than a second table. That keeps
    the number of things students have to think about right down.
    """

    CATEGORY_CHOICES = [
        ("cpu", "CPU"),
        ("gpu", "Graphics Card"),
        ("ram", "Memory"),
        ("storage", "Storage"),
        ("cooling", "Cooling"),
        ("case", "Case"),
        ("psu", "Power Supply"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(
        max_length=140,
        unique=True,
        help_text="A URL-friendly version of the name, e.g. 'ryzen-5-5600'.",
    )
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="other"
    )
    image = models.CharField(
        max_length=200,
        blank=True,
        help_text="Just the file name of an image in static/img, e.g. 'cpu-ryzen.svg'.",
    )
    stock = models.PositiveIntegerField(default=10)
    featured = models.BooleanField(
        default=False, help_text="Tick to show this on the home page."
    )

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:product_detail", kwargs={"slug": self.slug})


class Order(models.Model):
    """A single purchase made by a customer."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} - {self.customer.username}"

    @property
    def item_count(self):
        """How many physical things were bought (not how many line items)."""
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """One line on an order.

    We copy the price onto the order line on purpose. If a product price changes
    tomorrow, yesterday's receipt must still show what the customer actually paid.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def line_total(self):
        return self.price * self.quantity