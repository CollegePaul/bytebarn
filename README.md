# ByteBarn — a Django shop, built one small piece at a time

A teaching project for students. You build a small online computer shop: a
product list, a basket, customer accounts and a page that works out what a
built PC would cost.

Everything is done with **Django**, **Bootstrap 5** and **crispy-forms**. The
cost calculator is **plain JavaScript** — no framework, no external API, so it
works even when the school Wi-Fi does not.

---

## The finished site

| Page | What it does |
|------|--------------|
| Home | Hero banner and featured products |
| Shop | All products, filter by category, search by name |
| Product detail | One product, add to basket |
| Basket | Change quantities, remove, see the total |
| Checkout | Turns the basket into a real order in the database |
| PC Builder | Pick parts, live total, budget check — all in JavaScript |
| Register / Login | Customer accounts, forms styled with crispy-forms |
| Dashboard | Orders placed, total spent, recent orders |
| My orders | Full purchase history |
| Admin | `/admin/` — manage products and orders |

There is also a **superuser** account, which is a staff login for the admin site.

---

## How the guides work

Read them in order. Each one is a single small job that ends with something
working on your screen.

Every guide has:

- a **Mission** — what you are building
- numbered **Steps** with the exact commands to type
- **Checkpoints** — what you should see when it works
- **If something goes wrong** — for the mistakes everyone makes
- a **Mission complete** checklist
- a suggested **git commit** message

Guides are short on purpose. If a guide is taking more than about 45 minutes,
you are doing too much at once — stop, commit what works, and move on.

| # | Guide | Roughly |
|---|-------|---------|
| 00 | [Start here](docs/00-start-here.md) | 10 min |
| 01 | [Set up your environment](docs/01-set-up-your-environment.md) | 30 min |
| 02 | [Start the Django project](docs/02-start-the-django-project.md) | 30 min |
| 03 | [Your first template](docs/03-your-first-template.md) | 25 min |
| 04 | [Base template and navbar](docs/04-base-template-and-navbar.md) | 40 min |
| 05 | [The Product model and admin](docs/05-products-model-and-admin.md) | 45 min |
| 06 | [Load some sample data](docs/06-sample-data.md) | 20 min |
| 07 | [Product cards and filters](docs/07-product-cards.md) | 45 min |
| 08 | [The product page](docs/08-product-detail.md) | 30 min |
| 09 | [Register and log in](docs/09-register-and-login.md) | 45 min |
| 10 | [The dashboard](docs/10-dashboard.md) | 30 min |
| 11 | [The basket](docs/11-the-basket.md) | 50 min |
| 12 | [Checkout and purchase history](docs/12-orders-and-history.md) | 50 min |
| 13 | [The PC cost calculator](docs/13-pc-builder-calculator.md) | 45 min |
| 14 | [Tests and final checklist](docs/14-tests-and-checklist.md) | 30 min |
| 15 | [Stretch missions](docs/15-stretch-missions.md) | as long as you like |

---

## About the screenshots

The guides contain **real screenshots of this finished site**, taken from a
running copy of the exact code you will build. They are there so you can check
your work: *"my page should look like this"*.

They are not screenshots of VS Code or of the command prompt. Those parts are
shown as text, because that is clearer in a document anyway.

---

## Already in a hurry?

There is a working copy of the whole project in this repository. If you just
want to see the finished shop:

```bat
cd bytebarn
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_shop
python manage.py createsuperuser
python manage.py runserver
```

Then open <http://127.0.0.1:8000/>.

**Demo accounts** (created for this write-up, not part of the student build):

| Username | Password | What it is |
|----------|----------|------------|
| `shopadmin` | `admin12345` | Superuser — can use `/admin/` |
| `sam` | `testpassword123` | Customer with three orders already on their account |