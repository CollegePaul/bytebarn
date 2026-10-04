from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import RegisterForm


def register(request):
    """Create a customer account."""
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        # Log them straight in, so they do not have to type the password again.
        login(request, user)
        messages.success(request, f"Welcome to the shop, {user.first_name or user.username}!")
        return redirect("accounts:dashboard")

    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard(request):
    """The customer's own home page."""
    orders = request.user.orders.all()

    context = {
        "total_orders": orders.count(),
        "total_spent": sum(order.total for order in orders),
        "recent_orders": orders[:5],
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
def order_history(request):
    """Every order this customer has ever placed, newest first."""
    orders = request.user.orders.all()
    return render(request, "accounts/order_history.html", {"orders": orders})