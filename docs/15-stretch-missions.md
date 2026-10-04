# 15 — Stretch missions

**Mission:** you have finished. Now make it better.
**Time:** as long as you like

Pick **one**. Do not try to do them all. Each one is a self-contained change that
you can finish in a lesson and show off at the end.

---

## Tier 1 — Half an hour

### A. Sort the shop page

Right now products come back in whatever order `Product.Meta.ordering` says.

Add `?sort=price` and `?sort=name` support:

```python
SORT_OPTIONS = {
    "name": ["name"],
    "price": ["price"],
    "newest": ["-id"],
}
```

Read `request.GET.get("sort", "name")`, look it up, and pass
`ordering=...` to the queryset. Careful: **only use keys that are in your
dictionary**, never pass raw user input into `.order_by()`. Someone could type
`?sort=password` otherwise.

*Stretch:* keep the sort when the category filter changes.

### B. A "low stock" warning

On the product page, show a warning when fewer than five are left. On the shop
page, add a small badge. Try to do it in the template without changing the view.

### C. Low-stock report in the admin

Add a `LowStockProductAdmin` alongside the normal one, or a method on the model:

```python
@admin.display(boolean=True, description="In stock")
def in_stock(self, obj):
    return obj.stock > 0
```

*Stretch:* decorate it so low-stock products sort to the top.

### D. A 404 page that matches the site

Create `templates/404.html` extending `base.html`. Do the same for `500.html`.
They should still be readable when they are shown to a stranger.

### E. Remember the category when you come back

When someone clicks a product then presses *Back*, they lose their filter.
Add `?next=` to the product links and honour it on the product page.

---

## Tier 2 — a lesson or two

### F. Make stock safe ★

The comment in `checkout` says stock can go negative if two people buy the last
one at the same moment. Here is why:

```python
product.stock -= quantity    # read 1, write 0
product.save()               # ...two people do this at once
```

Django reads the row, changes it in Python, writes the whole row back. If both
requests read `stock = 1` before either writes, both write `0`, and you have
sold two of one thing.

The fix is `F()` expressions, which build the update in the database instead:

```python
from django.db.models import F

Product.objects.filter(pk=product.pk).update(
    stock=F("stock") - quantity
)
```

Now the database does `stock = stock - 1` as a single atomic operation.

**Then add a check.** After updating, look at the fresh stock and refuse the
order if it has gone below zero:

```python
Product.objects.filter(pk=product.pk).update(stock=F("stock") - quantity)
product.refresh_from_db()
if product.stock < 0:
    raise ValidationError("Not enough stock")
```

Because you are inside `transaction.atomic()`, raising rolls the whole order
back. That is what it is for.

> This is the best mission on the page. It teaches a real bug class that exists
> in real shops, and the fix is two lines.

### G. Search descriptions too ★

Currently `name__icontains=query` only looks at names. Change it so a search for
`"ray tracing"` finds the RTX 4060, whose description mentions ray tracing.

You will need `Q` objects:

```python
from django.db.models import Q

products = products.filter(
    Q(name__icontains=query) | Q(description__icontains=query)
)
```

*Stretch:* rank exact name matches above description matches.

### H. Let customers cancel an order ★

Add a "Cancel order" button on the receipt, available only while the status is
`pending` or `paid`.

The rules:
- `@require_POST` on the view
- `get_object_or_404(Order, pk=..., customer=request.user)` — **always**
- give the stock back
- send a flash message

Then add a test that a customer cannot cancel someone else's order.

### I. A profile page

Let customers change their first name and email.

The form:

```python
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "email"]
```

The view:

```python
@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})
```

Note `instance=request.user` — that is how you edit an existing object instead of
creating a new one. Add it to the navbar dropdown.

### J. Product images, properly ★

Right now `Product.image` is a text box holding a file name. That was a
deliberate shortcut to avoid installing Pillow and setting up uploads.

Now do it properly:

1. `pip install Pillow`
2. `image = models.ImageField(upload_to="products/", blank=True)`
3. In `settings.py`: `MEDIA_URL = "/media/"` and
   `MEDIA_ROOT = BASE_DIR / "media"`
4. In `config/urls.py`, add:

```python
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

5. Change the template to `{{ product.image.url }}`
6. Add `.gitignore` lines: `media/`
7. **Never** `ImageField()` on its own — always pair it with an `upload_to`.

*Stretch:* resize uploads in `Product.save()` so nothing bigger than 800px wide
goes into the database.

---

## Tier 3 — a proper project

### K. Make the calculator smarter ★★

Right now the total is just a sum. Make it useful:

- **Compatibility warnings.** "Your CPU is AMD and your motherboard is Intel" —
  you will need a motherboard slot.
- **A performance estimate.** Give each part a `performance_score` and show an
  overall score.
- **Save and share builds.** Store the choices in the session, give the build a
  code, and make `/builder/<code>/` load it again.
- **A "recommended" build.** Pick sensible parts for three budgets.

### L. Live prices from an API ★★

The version you built works offline, which is why it is safe in a classroom. If
you want to try a real API:

1. Find one (a price-comparison or currency API with a free tier).
2. Add a "Refresh prices" button.
3. `fetch()` the prices in JavaScript.
4. **Handle the failure.** It will fail one day. Show *"Prices unavailable, using
   our own prices"* rather than a blank page.

The interesting part is not the `fetch()` — it is the failure handling. Real
applications are mostly about what happens when something external breaks.

### M. Search with a real engine ★★

Install `django-haystack` and Elasticsearch, or use PostgreSQL's full-text
search with `SearchVector`. Note how much of the infrastructure that needs.

### N. Email order confirmations

Django's `send_mail` behind an `Order` save signal. Then try `console` as the
email backend in `settings.py` so you can read the emails without sending any.

---

## Tier 4 — the deep end

### O. Deploy it ★★

Take the project somewhere real. Things you must handle that you have been
ignoring:

- `DEBUG = False`
- A real `SECRET_KEY`, from an environment variable
- `ALLOWED_HOSTS` set to your real domain
- `python manage.py collectstatic` and a real static file server
- `python manage.py runserver` is **not** for production — use gunicorn or
  waitress
- HTTPS

Django's deployment checklist is long and worth reading:
<https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/>

### P. Switch to PostgreSQL ★★

SQLite is fine for a class and terrible for production. Move to PostgreSQL,
change the `DATABASES` setting, and move your data across with
`pg_dump`-style fixtures.

### Q. Write your own admin actions ★★

Bulk actions on the admin: "mark as shipped", "mark as cancelled". Look up
`@admin.action`.

### R. Pagination ★★

If the shop ever had 10,000 products, showing them all would be slow. Add
Django's `Paginator` to the shop page and give the tests a go.

### S. Learn enough to be dangerous ★★★

- Read the [Django tutorial](https://docs.djangoproject.com/en/5.1/tutorial/) —
  it builds a slightly different version of this project.
- Work through [Django for the impatient](https://djangoforimpatient.com/).
- Read `shop/views.py` and `shop/cart.py` until you can rewrite them from memory.

---

## How to present what you built

Two minutes, no slides. In order:

1. **The shop page.** Click a category, then a product.
2. **The basket.** Add two things, change a quantity.
3. **Register** an account in front of them.
4. **Check out**, and show the receipt.
5. **The dashboard** — orders placed, money spent.
6. **Log in as the superuser** and show `/admin/`.
7. **The PC Builder** — pick parts, set a budget of £700, and watch it say you
   are over.

Then: *"Here is a bug I found, here is the test that catches it, here is the fix."*

That last part is what marks a good project. A working site is the minimum. Being
able to say what you broke and how you know it is fixed is the difference.

---

## A note on where to go next

This project is deliberately small. If you want to keep going, the honest order
is:

1. **Make it deployable** (mission O). You will learn more in one afternoon of
   real deployment than in a term of theory.
2. **Add a real database** (mission P). SQLite is hiding things from you.
3. **Build something you actually want** — a recipe planner, a game scoreboard, a
   tool for your football team. The gap between "a tutorial project" and "my
   project" is where the learning happens.

Keep the same shape: small steps, commit after each one, write the test after you
fix the bug. That rhythm works for anything.