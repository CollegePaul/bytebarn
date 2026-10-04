from django.contrib import admin

from .models import Order, OrderItem, Product


class OrderItemInline(admin.TabularInline):
    """Show the order lines inside the order page, so staff only edit one page."""

    model = OrderItem
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "stock", "featured"]
    list_filter = ["category", "featured"]
    search_fields = ["name", "description"]
    list_editable = ["price", "stock", "featured"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "total", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["customer__username", "customer__email"]
    inlines = [OrderItemInline]