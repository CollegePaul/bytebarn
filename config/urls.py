"""URL configuration for the config project.

Three rules to remember:

1. Order matters. Django checks the list top to bottom and stops at the first
   match, so the specific ones go above the catch-all ones.
2. Every path can have a name. Names are safer than URLs because if you change
   the URL later, you only change it in this file.
3. include() means "go and look in that app's urls.py".
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # The admin site, at /admin/
    path("admin/", admin.site.urls),

    # Django's own login / logout / change-password pages.
    # That gives us /accounts/login/, /accounts/logout/ and so on, for free.
    path("accounts/", include("django.contrib.auth.urls")),

    # Our own accounts pages (register, dashboard, orders).
    path("accounts/", include("accounts.urls")),

    # Everything else belongs to the shop app, so / goes straight there.
    path("", include("shop.urls")),
]