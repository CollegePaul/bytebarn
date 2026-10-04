from django.urls import path

from . import views

# The name= on each path is how we refer to a URL from a template or from
# another view, e.g. {% url 'shop:product_detail' product.slug %}. Change the
# URL in views.py by changing this file, and every link updates itself.

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.product_list, name="product_list"),
    path("shop/<slug:slug>/", views.product_detail, name="product_detail"),
    path("builder/", views.builder, name="builder"),
    path("builder/add-to-cart/", views.builder_add_to_cart, name="builder_add_to_cart"),
    path("basket/", views.cart_view, name="cart"),
    path("basket/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("basket/update/", views.cart_update, name="cart_update"),
    path("basket/remove/<int:pk>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
]