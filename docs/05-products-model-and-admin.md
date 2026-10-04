# 05 — The Product model, migrations and admin

**Mission:** define what a product *is*, tell the database about it, and create a superuser so you can add products by clicking.
**Time:** about 45 minutes
**You will have when you finish:** a real database with products in it, editable at `/admin/`.

---

## Before you start

- Guides 01–04 are finished and committed
- `python manage.py runserver` is running

---

## Step 1 — Write the Product model

A **model** is a Python class that describes a kind of thing you want to store.
Django reads it and builds a database table from it.

Open `shop/models.py` and replace the file with:

```python
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
```

### Walking through it

| Line | What it means |
|------|---------------|
| `class Product(models.Model)` | "products are the kind of thing we store" |
| `name = models.CharField(max_length=120)` | a text box, up to 120 characters |
| `slug = models.SlugField(unique=True)` | a URL-friendly name, and no two may match |
| `description = models.TextField(blank=True)` | a big box; `blank=True` means it may be empty |
| `price = models.DecimalField(max_digits=8, decimal_places=2)` | up to 999999.99 — **not** a float |
| `choices=CATEGORY_CHOICES` | only these values are allowed, from a dropdown |
| `stock = models.PositiveIntegerField(default=10)` | a whole number, never negative |
| `class Meta: ordering = [...]` | new products come back sorted, not in random order |

> **Why `DecimalField` and not `FloatField`?** Because floating point numbers
> cannot represent 19.99 exactly. `19.99 + 0.01` gives `20.000000000000004`.
> Money must never use floats. Django will not let you get this wrong by
> accident, which is the whole point.

> **What is a slug?** `/shop/amd-ryzen-5-5600/` reads nicely and contains no
> spaces or slashes. We use it in the address bar in Guide 08.

### Why `__str__`?

`__str__` tells Python what to print when you look at an object. Without it,
Django's admin and error messages show `Product object (1)`. With it they show
`AMD Ryzen 5 5600`. Two lines, huge difference when you are debugging.

---

## Step 2 — Make the migration

```bat
python manage.py makemigrations shop
```

**Checkpoint:**

```
Migrations for 'shop':
  shop/migrations/0001_initial.py
    + Create model Product
```

> **Read this name carefully: `makemigrations` writes a file. It does not change
> your database.** Writing the change down and applying the change are two
> separate steps, on purpose. That is what lets your teacher see, review and
> roll back every change you have made to the shape of your data.

```bat
python manage.py migrate
```

**Checkpoint:**

```
Applying shop.0001_initial... OK
```

You should now have a file called `db.sqlite3` in your project. That is your
database — the whole thing, in one file. Back it up by copying it somewhere
safe.

> **Never commit `db.sqlite3` to git.** Your `.gitignore` from Guide 01 already
> ignores it. Migrations are the real history; the database is disposable.

---

## Step 3 — Create a superuser

A **superuser** is the staff account for Django's admin site. It is not a
customer.

```bat
python manage.py createsuperuser
```

It asks three questions. Answer them like this:

```
Username: shopadmin
Email address: shop@example.com
Password: **********
Password (again): **********
```

> **Use the same password for everyone in the class** if you are sharing
> details, and say it out loud. It is a practice shop; nobody is protecting
> anything.

**Checkpoint.** `Superuser created successfully.`

> **If it says "command not found" or gives a weird error**, your virtual
> environment is off. `.venv\Scripts\activate` and try again.

---

## Step 4 — Log in to the admin

Open <http://127.0.0.1:8000/admin/> and log in.

**Checkpoint.** You see the Django administration site with two sections:
*Authentication and Authorization* (Groups, Users) and *Shop*.

But there are no products listed yet, because we have not told Django that
Product should appear here.

---

## Step 5 — Register the model

Open `shop/admin.py` and replace it with:

```python
from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "stock", "featured"]
    list_filter = ["category", "featured"]
    search_fields = ["name", "description"]
    list_editable = ["price", "stock", "featured"]
    prepopulated_fields = {"slug": ("name",)}
```

**Checkpoint.** Save it, refresh `/admin/`, and *Shop → Products* now has a
link. Click **Add product**.

---

## Step 6 — Add your first product by hand

Fill in the form:

| Field | Value |
|-------|-------|
| Name | `AMD Ryzen 5 5600` |
| Slug | `amd-ryzen-5-5600` |
| Description | `Six cores, twelve threads. The best-value gaming CPU of its generation and still easy to cool.` |
| Price | `129.99` |
| Category | `CPU` |
| Stock | `12` |
| Featured | ticked |
| Image | *(leave blank for now)* |

Click **Save**.

**Checkpoint.** You are back on the product list, with one row. You can edit the
price and stock **directly in that table** — that is `list_editable`. The
`category` and `featured` columns on the right are clickable filters.

> **The slug filled itself in.** That is `prepopulated_fields`. It slugs the Name
> field for you as you type, which saves a lot of typing and stops typos.

Now add four or five more products by hand, one in each of a few categories. Use
made-up-but-plausible names and prices. Keep them realistic — you will build the
calculator around them later.

---

## Step 7 — Look at it in the shell

The **shell** is a Python prompt that knows about your project. It is the
fastest way to ask questions of your data.

```bat
python manage.py shell
```

You should see a `>>>` prompt. Type:

```python
>>> Product.objects.count()
6
>>> product = Product.objects.get(slug="amd-ryzen-5-5600")
>>> product.name
'AMD Ryzen 5 5600'
>>> product.price
Decimal('129.99')
>>> product.get_category_display()
'CPU'
>>> Product.objects.filter(featured=True)
<QuerySet [<Product: AMD Ryzen 5 5600>, ...]>
```

That last line is worth pausing on. `filter()` asks the database for matching
rows. A **QuerySet** is a lazy list — it has not fetched anything yet, which is
why Django can be so fast.

Type `exit()` to leave.

> **A tip that saves hours.** When you want to see what a database query returns,
> use the shell. It answers in one second. The admin page takes ten and will not
> tell you why something is missing.

---

## Mission complete

- [ ] `shop/models.py` defines a `Product` with the fields listed above
- [ ] `python manage.py makemigrations shop` created `0001_initial.py`
- [ ] `python manage.py migrate` applied it
- [ ] `db.sqlite3` exists and is in your `.gitignore`
- [ ] You have a superuser and can log in at `/admin/`
- [ ] `/admin/shop/product/` lists your products
- [ ] You have added at least five products by hand
- [ ] You have run a query in `python manage.py shell`

**Commit:** `git commit -m "Guide 05: product model, migrations and admin"`

---

## If something goes wrong

**`makemigrations` says `No changes detected`**
You did not save `models.py`, or you did not change anything.

**`You have N unapplied migration(s)`**
Run `python manage.py migrate`.

**`FieldError: Cannot resolve keyword 'featured' into field`**
The name is spelled differently in the model than in your query. Check for
typos — `featured`, not `featured=True`.

**`DoesNot exist` in the shell**
There is no product with that slug. Run `print(Product.objects.all())` and look
at what you actually have.

**`createsuperuser` says the username is taken**
Use a different one, or delete the database and start over:
`del db.sqlite3` then `python manage.py migrate`.

**I want to start the database again**
Stop the server, run `del db.sqlite3`, then `python manage.py migrate` and
`python manage.py createsuperuser` again. You lose all your products — which is
why Guide 06 gives you a way of putting them all back in one command.

**The admin has no `Shop` section**
`shop/admin.py` does not import the model, or you forgot the `@admin.register`
decorator, or the server needs restarting.

**`decimal.InvalidOperation` when typing a price**
Type digits only — no `£` sign. The symbol is added by the template.

---

Next: [06 — Load some sample data](06-sample-data.md)