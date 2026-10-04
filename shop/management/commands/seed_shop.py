"""Fill the shop with sample products.

Run it with:

    python manage.py seed_shop

Running it twice will not create duplicates -- it matches on the slug and
updates whatever is already there.
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
        "description": "Six cores, twelve threads. The best-value gaming CPU of "
        "its generation and still easy to cool.",
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
    {
        "slug": "nvidia-rtx-4060",
        "name": "NVIDIA GeForce RTX 4060",
        "category": "gpu",
        "price": "279.99",
        "stock": 6,
        "featured": True,
        "image": "gpu-rtx4060.svg",
        "description": "Ray tracing and DLSS in a short, cool-running card. A "
        "solid 1080p workhorse.",
    },
    {
        "slug": "amd-radeon-rx-7600",
        "name": "AMD Radeon RX 7600",
        "category": "gpu",
        "price": "219.99",
        "stock": 9,
        "featured": False,
        "image": "gpu-rx7600.svg",
        "description": "Great raw raster performance for the money. 8GB of "
        "video memory, plenty for 1440p gaming.",
    },
    {
        "slug": "corsair-vengeance-16gb",
        "name": "Corsair Vengeance 16GB DDR4",
        "category": "ram",
        "price": "39.99",
        "stock": 25,
        "featured": True,
        "image": "ram-16gb.svg",
        "description": "2 x 8GB sticks running at 3200MHz. Sixteen gigabytes is "
        "the sweet spot for most builds.",
    },
    {
        "slug": "kingston-fury-32gb",
        "name": "Kingston Fury 32GB DDR4",
        "category": "ram",
        "price": "74.99",
        "stock": 15,
        "featured": False,
        "image": "ram-32gb.svg",
        "description": "2 x 16GB at 3200MHz. Worth it if you edit video or run "
        "lots of browser tabs.",
    },
    {
        "slug": "samsung-970-evo-plus-1tb",
        "name": "Samsung 970 EVO Plus 1TB",
        "category": "storage",
        "price": "64.99",
        "stock": 20,
        "featured": True,
        "image": "ssd-1tb.svg",
        "description": "NVMe M.2 drive at up to 3500MB/s. Your operating system "
        "and games should live on this, not the hard disk.",
    },
    {
        "slug": "seagate-barracuda-2tb",
        "name": "Seagate BarraCuda 2TB",
        "category": "storage",
        "price": "54.99",
        "stock": 18,
        "featured": False,
        "image": "hdd-2tb.svg",
        "description": "A spinning hard disk. Slow, but cheap per gigabyte. "
        "Good for backups and media libraries.",
    },
    {
        "slug": "fractal-pop-air-case",
        "name": "Fractal Design Pop Air",
        "category": "case",
        "price": "69.99",
        "stock": 10,
        "featured": False,
        "image": "case-tower.svg",
        "description": "Compact mid tower with a mesh front panel and three fans "
        "included as standard.",
    },
    {
        "slug": "corsair-rm750e",
        "name": "Corsair RM750e 750W",
        "category": "psu",
        "price": "79.99",
        "stock": 14,
        "featured": True,
        "image": "psu-750.svg",
        "description": "80 Plus Gold, fully modular. 750W is plenty for almost "
        "any single-GPU build.",
    },
    {
        "slug": "arctic-p12-fan-pack",
        "name": "Arctic P12 Fan Pack of 3",
        "category": "cooling",
        "price": "14.99",
        "stock": 30,
        "featured": False,
        "image": "fan-pack.svg",
        "description": "Three quiet 120mm case fans. Hard to beat for the price.",
    },
    {
        "slug": "amd-wraith-stealth",
        "name": "AMD Wraith Stealth Cooler",
        "category": "cooling",
        "price": "19.99",
        "stock": 22,
        "featured": False,
        "image": "cooler-air.svg",
        "description": "The cooler that ships in the box with most AMD CPUs. "
        "Quiet, and it will not block the first RAM slot.",
    },
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
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing products."))

        created_count = 0
        updated_count = 0

        for data in PRODUCTS:
            data = dict(data, price=Decimal(data["price"]))
            slug = data.pop("slug")

            product, created = Product.objects.update_or_create(slug=slug, defaults=data)

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