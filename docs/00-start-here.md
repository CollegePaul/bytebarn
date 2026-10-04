# 00 — Start here

**Time:** about 10 minutes of reading
**You will have when you finish:** a clear plan, and nothing installed yet

---

## What you are building

A small online shop that sells computer parts. It has:

- a **home page** with featured products
- a **shop page** showing every product, with filters
- a **basket** that remembers what you put in it
- **customer accounts** — register, log in, see your own dashboard
- **purchase history** — every order you have ever placed
- a **PC cost calculator** that adds up a build in your browser
- an **admin site** where staff can add products and see orders

It uses Django for the back end, Bootstrap for the look, crispy-forms for the
forms, and plain JavaScript for the calculator.

---

## The rules for this project

These are the rules that make the project stay small. Follow them and you will
finish. Break them and you will spend three evenings on CSS instead of learning.

**1. Functionality beats looks.**
The site should *work* before it should be pretty. If you have to choose
between making the basket work and making the buttons rounder — basket.

**2. One guide, one sitting.**
Each guide is a small job. Do it, check the checkpoints, commit, move on. Do not
try to jump ahead and come back later; the guides build on each other.

**3. Small steps, committed often.**
After every guide:

```bat
git add .
git commit -m "Guide 03: first template"
```

If you break something later, this is how you get back to working.

**4. Do not fight a red error for more than 15 minutes.**
Read the message properly — it usually says exactly what is wrong and where.
Then look at the **If something goes wrong** section at the bottom of the guide.
Then ask. Getting stuck is normal; getting stuck alone is the problem.

**5. Read the code that is already there.**
Every file in this project is commented, and the comments explain *why*, not
just *what*. When you finish a guide, open the files you created and re-read
them.

---

## How a Django request works

You will see this picture over and over. Worth understanding now rather than in
week three.

```
   Someone types  /shop/  into the browser
                │
                ▼
   ┌─────────────────────────┐
   │  config/urls.py         │  "which view handles /shop/ ?"
   │  shop/urls.py           │
   └─────────────────────────┘
                │
                ▼
   ┌─────────────────────────┐
   │  shop/views.py          │  Python runs. It asks the database for
   │  product_list()         │  the products it needs.
   └─────────────────────────┘
                │
                ▼
   ┌─────────────────────────┐
   │  shop/models.py         │  the database: products, orders
   └─────────────────────────┘
                │
                ▼
   ┌─────────────────────────┐
   │  templates/shop/        │  the data goes into a template,
   │  product_list.html      │  which gets turned into HTML
   └─────────────────────────┘
                │
                ▼
        the browser shows the page
```

Five pieces, always in the same order. Every guide adds one of them.

---

## The project map

Get this picture in your head now and the rest is much easier.

```
bytebarn/
│
├── manage.py                  a command you type into cmd
├── requirements.txt           the list of packages to install
│
├── config/                    the project itself (the "settings" folder)
│   ├── settings.py            ← what you will edit most
│   ├── urls.py                ← the table of contents of your website
│   └── wsgi.py                ignore this
│
├── shop/                      everything about buying things
│   ├── models.py              ← Product, Order, OrderItem
│   ├── views.py               ← what each page does
│   ├── urls.py                ← this app's addresses
│   ├── cart.py                ← the basket (kept in the session)
│   ├── admin.py               ← how products look in /admin/
│   ├── forms.py               (we do not need one yet)
│   ├── tests.py               the checks that prove it works
│   └── management/commands/
│       └── seed_shop.py       ← loads the sample products
│
├── accounts/                  everything about customers
│   ├── forms.py               ← the register form
│   ├── views.py               ← register, dashboard, order history
│   └── urls.py
│
├── templates/                 all the HTML
│   ├── base.html              ← the frame every page sits inside
│   ├── shop/                  home, product list, basket, builder, receipt
│   ├── accounts/              register, dashboard, order history
│   └── registration/          login, logged out, change password
│
├── static/                    all the CSS, JS and images
│   ├── css/style.css
│   ├── js/builder.js          ← the cost calculator
│   └── img/*.svg
│
├── docs/                      ← you are reading this
└── db.sqlite3                 your database, created automatically
```

---

## What you need

- A computer running **Windows 10 or 11**
- About **2 GB** of free disk space
- Internet access for the very first setup, then not much after that

You do **not** need to know HTML, CSS, JavaScript or Python beforehand. You do
need to be comfortable opening a command prompt and following instructions.

---

## Ready?

Go to [01 — Set up your environment](01-set-up-your-environment.md).

---

## If you want to peek first

If you would rather see where this is going, the finished site is described in
the [project README](../README.md). You can always come back here afterwards.