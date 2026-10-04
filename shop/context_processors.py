from django.conf import settings
from django.db import transaction

from .cart import cart_count


def shop(request):
    """Extra bits of information that every single template needs.

    Adding a context processor here means the basket badge works on every page
    without us passing anything into each view by hand.
    """
    return {
        "cart_count": cart_count(request),
        "currency": settings.SHOP_CURRENCY,
    }