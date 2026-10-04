# 06 — Product images and sample data

**Mission:** add pictures for your products, then load twelve real products with a single command instead of clicking.
**Time:** about 20 minutes
**You will have when you finish:** a shop full of products, and a `seed_shop` command you can run again any time.

---

## Before you start

- Guide 05 is finished and committed
- You have at least a few products in `/admin/`

---

## Step 1 — Put the images in place

The product model stores images as **file names**, not as uploads:

```python
image = models.CharField(
    max_length=200,
    blank=True,
    help_text="Just the file name of an image in static/img, e.g. 'cpu-ryzen.svg'.",
)
```

So a product with `image` set to `cpu-ryzen.svg` will show
`/static/img/cpu-ryzen.svg`.

Copy the supplied pictures into your static folder:

```bat
xcopy docs\starter-files\img\*.svg static\img\
```

Or just drag the twelve `.svg` files from `docs/starter-files/img/` into
`static/img/` in VS Code.

**Checkpoint.** `static/img/` now contains files like `cpu-ryzen.svg`,
`gpu-rtx4060.svg`, `ram-16gb.svg`.

### What is an SVG?

**S**tructured **V**ector **G**raphics — a picture made of shapes described in
XML. Zoom in and it stays sharp. They are tiny (a few hundred bytes), they need
no internet connection, and you can open one in Notepad and change the colours.

Here is the whole of one:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
  <rect width="400" height="300" fill="#0f2942"/>
  <rect x="135" y="95" width="130" height="130" rx="10" fill="#e2e8f0"/>
</svg>
```

**Mission:** open `cpu-ryzen.svg` in VS Code, change `#0f2942` to `#7f1d1d`
(dark red), save, and refresh `/admin/`. The background turns red. That is the
whole idea of SVG — it is text.

> **Using your own images instead?** Save any picture into `static/img/` and put
> its file name in the product's Image field. `photo.png` is fine too. The
> `.svg` files are just so the screenshots in these guides match.

---

## Step 2 — Build a management command

Typing twelve products into the admin form takes about twenty minutes and you
would have to do it again on every new machine. A **management command** is a
piece of Python you run with `manage.py` instead of clicking.

### Make the folders

Django only looks for commands in a particular place, so the folders must be
named exactly:

```
shop/
└── management/
    └── commands/
        └── seed_shop.py
```

Right-click `shop` → **New Folder** → `management`. Inside that, **New Folder** →
`commands`. Inside *that*, **New File** → `__init__.py`. Do the same for
`__init__.py` in `management`.

You end up with:

```
shop/management/__init__.py
shop/management/commands/__init__.py
```

Those empty files are what tell Python "this folder is part of the project".

### Write the command

In `shop/management/commands/seed_shop.py`:

```python
"""Fill the shop with sample products.

Run it with:

    python manage.py seed_shop
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from shop.models import Product

PRODUCTS = [
    {
        "slug": "amd-ryzen-5-5600",
        "name": "AMD Ryzen 5 5600",
        "category": "cpu",
        "price": "129.99",
        "stock": 12,
        "featured": True,
        "image": "cpu-ryzen.svg",
        "description": "Six cores, twelve threads. The best-value gaming CPU "
        "of its generation and still easy to cool.",
    },
    {
        "slug": "intel-core-i5-12400f",
        "name": "Intel Core i5-12400F",
        "category": "cpu",
        "price": "139.99",
        "stock": 8,
        "featured": False,
        "image": "cpu-intel.svg",
        "description": "Six performance cores with a boost clock of 4.4GHz. "
        "No integrated graphics, so you will need a graphics card.",
    },
    # ... nine more, in the same shape ...
]


class Command(BaseCommand):
    help = "Load sample products into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete every existing product first.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            deleted, _ = Product.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f"Deleted {deleted} existing products.")
            )

        created_count = 0
        updated_count = 0

        for data in PRODUCTS:
            data = dict(data, price=Decimal(data["price"]))
            slug = data.pop("slug")

            product, created = Product.objects.update_or_create(
                slug=slug, defaults=data
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created {created_count}, updated {updated_count}. "
                f"The shop now has {Product.objects.count()} products."
            )
        )
```

> **Grab the full list.** The finished project has all twelve entries in
> `shop/management/commands/seed_shop.py` — copy them in. Or write three or four
> yourself and run it; that is enough to carry on.

### Three things worth understanding

**`class Command(BaseCommand)`** — this is the whole convention. Django finds the
class, calls `handle()`, and the name of the file is the name of the command.
`seed_shop.py` → `python manage.py seed_shop`.

**`Decimal(data["price"])`** — we store prices as text in the list for
readability, then convert. Prices are `DecimalField`, not floats.

**`update_or_create`** — looks for a product with that slug. If it exists, update
it; if not, create it. So you can run the command as many times as you like
without creating duplicates. That is far friendlier than a plain `.create()`.

---

## Step 3 — Run it

```bat
python manage.py seed_shop
```

**Checkpoint:**

```
Done. Created 12, updated 0. The shop now has 12 products.
```

Look at `/admin/shop/product/`. Twelve rows, with pictures if you clicked *Featured*
column, filters on the right.

Run it again:

```bat
python manage.py seed_shop
```

```
Done. Created 0, updated 12. The shop now has 12 products.
```

**Still twelve.** That is `update_or_create` doing its job.

To wipe the shop and start again:

```bat
python manage.py seed_shop --clear
```

---

## Step 4 — Point the products at their images

The command already sets `image` for each product. Check one at
`/admin/shop/product/` — the field should say `cpu-ryzen.svg`.

Open `/admin/shop/product/1/change/` and look at the **image** box. It is a plain
text box, not a file picker. That is deliberate:

- no file uploads to set up
- no Pillow library to install
- no `MEDIA_URL`, no `MEDIA_ROOT`, no extra settings

The trade-off is that if a file goes missing you get a broken image. We guard
against that in the card template in Guide 07.

---

## If something goes wrong

**`CommandError: Unknown command: 'seed_shop'`**
The file is in the wrong place, or `__init__.py` is missing. It must be
`shop/management/commands/seed_shop.py` with both `__init__.py` files.

**`ImportError: cannot import name 'Product' from 'shop.models'`**
Check the import at the top of `seed_shop.py`.

**`decimal.InvalidOperation`**
A price in your list has something other than a number in it — no `£`, no
letters, no commas.

**`ValidationError` or `IntegrityError` on slug**
Two products in your list have the same slug. Every slug must be unique.

**Products appear but with no pictures**
The `.svg` files did not get copied into `static/img/`. Copy them again and
check the browser's Network tab for a 404 on `/static/img/...`.

**Images show a broken icon**
The `image` field says something like `ryzen.jpg` but the file is called
`cpu-ryzen.svg`. The field is an exact file name — including the extension.

---

Next: [07 — Product cards and filters](07-product-cards.md)