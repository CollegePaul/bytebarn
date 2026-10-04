# 03 — Your first template

**Mission:** make the home page say "Hello", and put a stylesheet next to it.
**Time:** about 25 minutes
**You will have when you finish:** a real page, built from a URL, a view and a template.

---

## Before you start

- `python manage.py runserver` is running in one command prompt
- You are editing files in VS Code

---

## What is a view, and what is a template?

Django does not put HTML in your Python files. It keeps them apart:

- a **view** is a Python function that decides *what data* the page needs
- a **template** is an HTML file with holes in it where the data goes

```
  /            →  urls.py  →  views.home()  →  templates/shop/home.html
```

One view, one template. That split is the single most useful habit in Django.

---

## Step 1 — Write the view

Open `shop/views.py`. Replace the whole file with:

```python
from django.shortcuts import render

# --- Pages anybody can see ----------------------------------------------------


def home(request):
    """The landing page."""
    return render(request, "shop/home.html")
```

Read it as English: *"take the request, render the file templates/shop/home.html,
send the result back."*

> **`request`** is the browser's request — it carries the URL, the cookies, who is
> logged in. You need it almost every time. We do not use it here yet.

---

## Step 2 — Tell Django where `/` goes

Create a file called `shop/urls.py` (it does not exist yet — VS Code will not
offer "New File" for it, so right-click the `shop` folder → **New File** and type
`urls.py`):

```python
from django.urls import path

from . import views

# The name= on each path is how we refer to a URL from a template, so we never
# hard-code addresses in our HTML.

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
]
```

`app_name` creates a little namespace. From now on the home page is called
`shop:home` in templates and views. That stops two apps having a `home` URL and
clashing.

---

## Step 3 — Point the project at the app's URLs

Open `config/urls.py` and replace it with:

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # The admin site, at /admin/
    path("admin/", admin.site.urls),

    # Everything else belongs to the shop app, so / goes straight there.
    path("", include("shop.urls")),
]
```

> **`include()` means "go and look in that app's urls.py".** Without it Django
> never finds your `path("", views.home)`.

**Checkpoint.** Save, and <http://127.0.0.1:8000/> now shows an error page:

```
TemplateDoesNotExist at /
```

That is a **good** sign. It means the URL works and the view runs. It just has
no template yet. If you were still seeing the Django welcome page, your
`urls.py` was not picked up.

---

## Step 4 — Write the template

Create `templates/shop/home.html` (make the `shop` folder inside `templates`
first). Start with the smallest possible thing:

```html
<h1>ByteBarn</h1>
<p>PC parts without the guesswork.</p>
```

**Checkpoint.** Save and refresh the browser:

```
ByteBarn
PC parts without the guesswork.
```

No styling at all — deliberately. We have proved the whole chain works: browser
→ URL → view → template → page. Everything else is decoration on top.

> **About `request` in `render`.** Some people write `render(request, "home.html")`
> and some write `render("home.html")`. The first is correct in modern Django.
> If you see a tutorial using the short form, it is old.

---

## Step 5 — Give it a proper HTML skeleton

Replace `templates/shop/home.html` with:

```html
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ByteBarn</title>
</head>

<body>
  <h1>ByteBarn</h1>
  <p>PC parts without the guesswork.</p>
</body>

</html>
```

**Checkpoint.** View source (<kbd>Ctrl</kbd>+<kbd>U</kbd>) and you can see the
full document. Still unstyled — that is next.

---

## Step 6 — Add Bootstrap

Bootstrap is a big file of CSS written by other people. You do not install it —
you link to it from a **CDN** (Content Delivery Network), which is just a website
that hosts the file for you.

Add one line inside `<head>`, above `</head>`:

```html
  <!-- Bootstrap from a CDN: no install, always up to date -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
```

**Checkpoint.** Still plain, because we have no Bootstrap classes yet. Add one:

```html
<div class="container py-5">
  <h1 class="display-3 fw-bold">ByteBarn</h1>
  <p class="lead text-body-secondary">PC parts without the guesswork.</p>
  <button class="btn btn-primary">Browse the shop</button>
</div>
```

Refresh. **Checkpoint:** the heading is now huge, the text is grey, and the
button is blue and rounded. You have styling, and you wrote none of it.

> **The Bootstrap idea in one line:** nearly every class name describes what
> something should *look* like, not what it *is*. `text-danger` makes text red.
> `btn` makes a button. `d-flex` puts children in a row. You never write CSS for
> these — you just use the name.

---

## Step 7 — Add your own stylesheet

We still need one thing Bootstrap cannot do: our own colours and spacing.

Create `static/css/style.css`:

```css
/* ByteBarn styling.
   Bootstrap does almost everything. This file is only for the few things
   Bootstrap has no class for. Keep it short on purpose. */

body {
  background-color: #f8f9fa;
}
```

Now tell the template about it. **Two changes** — Django's `{% static %}` tag and
your file:

At the very top of the template, *above* the `<!DOCTYPE>`:

```html
{% load static %}
```

And in `<head>`, after the Bootstrap line:

```html
  <link rel="stylesheet" href="{% static 'css/style.css' %}">
```

**Checkpoint.** Refresh. The page background is now very slightly grey. Hard to
notice? Good — that is what you want from your own CSS. Make it obvious on
purpose by changing the colour to `hotpink` and refreshing. Once you have seen it
work, change it back.

> **`{% load static %}` must be at the top of the template.** A template has to
> *declare* that it wants to use a tag library before it can use the tags from
> it. This catches everybody.

---

## Step 8 — Pass something from the view to the template

Right now the template is completely static. Let us put a hole in it.

In `shop/views.py`:

```python
from django.shortcuts import render


def home(request):
    """The landing page."""
    shop_name = "ByteBarn"
    return render(request, "shop/home.html", {"shop_name": shop_name})
```

The `{"shop_name": shop_name}` at the end is the **context**: the dictionary of
data the view hands to the template.

In the template, use the variable with double curly braces:

```html
<h1>{{ shop_name }}</h1>
```

**Checkpoint.** The page still says ByteBarn — but now it is coming from Python.

Try breaking it on purpose: change the Python to `"Byte Barn"` with a space and
refresh. You should see the space. Double curly braces `{{ }}` print a value.
Curly braces with a percent `{%%}` are commands like our `{% load %}`.

---

## Mission complete

- [ ] `shop/urls.py` exists and points `/` at `views.home`
- [ ] `config/urls.py` includes `shop.urls`
- [ ] <http://127.0.0.1:8000/> shows your heading, not an error
- [ ] The page has a full HTML skeleton and loads Bootstrap
- [ ] `static/css/style.css` exists and is linked with `{% static %}`
- [ ] The shop name comes from a variable passed by the view
- [ ] You know the difference between `{{ }}` and `{%% %}`

**Commit:** `git commit -m "Guide 03: first template"`

---

## If something goes wrong

**`TemplateDoesNotExist`**
The path is wrong or the file is in the wrong place. It must be
`templates/shop/home.html`, and `TEMPLATES["DIRS"]` must contain
`[BASE_DIR / "templates"]` from Guide 02. Check for a capital `T` in
`templates` — Windows hides that mistake surprisingly well.

**`NoReverseMatch: Reverse for 'shop:home' not found`**
Something references a URL name that does not exist yet. Check the spelling and
that `shop/urls.py` really has `name="home"`.

**Still seeing the Django welcome page**
Your `path("", include("shop.urls"))` is missing or misspelled in
`config/urls.py`.

**Bootstrap styles do not appear at all**
Check the `<link>` tag is inside `<head>` and that you saved the file. If the
rest of the page is styled but the page looks plain, your school network is
blocking the CDN — tell your teacher, it is a known issue.

**Images or CSS return 404 in the browser's console**
You skipped `STATICFILES_DIRS` in Guide 02, step 4c.

**`ImportError: cannot import name 'home' from 'shop'**
Your view is not called `home`, or it is not saved.

---

Next: [04 — Base template and navbar](04-base-template-and-navbar.md)