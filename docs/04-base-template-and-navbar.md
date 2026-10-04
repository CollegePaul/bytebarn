# 04 — Base template and navbar

**Mission:** build one `base.html` that every page sits inside, with a navigation bar, flash messages and a footer.
**Time:** about 40 minutes
**You will have when you finish:** a navbar with working links, and templates that no longer repeat themselves.

---

## Before you start

- Guide 03 is finished and committed
- Your home page shows a Bootstrap-styled heading

---

## The problem we are solving

Right now `home.html` contains the `<html>`, `<head>` and Bootstrap link. When we
add a shop page, we would have to copy all of that into it. Change the navbar
later and you would have to edit every file.

So we make **one template that others fill in**.

```
templates/
├── base.html          the frame: doctype, head, navbar, footer
├── shop/
│   └── home.html      just the bits that are different
└── accounts/
    └── dashboard.html
```

---

## Step 1 — Create `base.html`

Make `templates/base.html`:

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}ByteBarn{% endblock %}</title>

  <!-- Bootstrap from a CDN: no install, always up to date -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

  <!-- Our own tiny bit of styling, on top of Bootstrap -->
  <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>

<body>

  <!-- The page content goes here -->
  <main class="container py-4">
    {% block content %}{% endblock %}
  </main>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  {% block scripts %}{% endblock %}
</body>

</html>
```

### What are those `{% block %}` things?

A **block** is a named hole. `{% block content %}{% endblock %}` says *"put
whatever the child template puts here"*. The `{% endblock %}` marks where the
hole ends.

```
base.html
  <main>
    {% block content %}{% endblock %}   ← the hole
  </main>
```

---

## Step 2 — Make `home.html` fill in the hole

Replace `templates/shop/home.html` with:

```html
{% extends "base.html" %}

{% block content %}
  <div class="hero p-4 p-lg-5 mb-4">
    <h1 class="display-5 fw-bold">ByteBarn</h1>
    <p class="lead mb-3">PC parts without the guesswork.</p>
    <a href="#" class="btn btn-primary btn-lg">Browse the shop</a>
  </div>
{% endblock %}
```

Two new things:

- `{% extends "base.html" %}` — *"this page is built on top of that one"*
- everything else is now **inside** `{% block content %}`

**Checkpoint.** The page still looks right, and `{% block title %}` is empty so
the title is still ByteBarn.

> **Rule:** in a child template, everything outside a `{% block %}` is thrown
> away. If you put text in `home.html` but not inside a block, it will not
> appear. This is the single most common beginner surprise in Django templates.

> **Order matters:** `{% extends %}` must be the first tag in the file.

### Give the page its own title

Add this to the top of `home.html`, above the content block:

```html
{% block title %}ByteBarn — PC parts without the guesswork{% endblock %}
```

**Checkpoint.** The browser tab now shows your new title. That is
`{% block title %}` from `base.html` being overridden.

---

## Step 3 — Build the navbar

Find this in `base.html`:

```html
  <!-- The page content goes here -->
```

and put the navbar **above** it:

```html
  <!-- ================= NAVBAR ================= -->
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <a class="navbar-brand fw-bold" href="{% url 'shop:home' %}">ByteBarn</a>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
              data-bs-target="#mainNav" aria-controls="mainNav" aria-expanded="false"
              aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="mainNav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <a class="nav-link" href="{% url 'shop:product_list' %}">Shop</a>
          </li>
        </ul>

        <ul class="navbar-nav">
          <li class="nav-item">
            <a class="nav-link" href="{% url 'login' %}">Log in</a>
          </li>
          <li class="nav-item">
            <a class="btn btn-primary btn-sm ms-2" href="#">Register</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <!-- The page content goes here -->
```

**Checkpoint.** A dark bar across the top with *ByteBarn*, *Shop* and
*Log in / Register*. Shrink your browser window and the links collapse behind a
three-line button — that is Bootstrap's JavaScript doing it, which is why we
loaded `bootstrap.bundle.min.js` at the bottom.

### About those mysterious class names

| Class | What it does |
|-------|--------------|
| `navbar navbar-expand-lg` | the bar; expand when the screen is large |
| `navbar-dark bg-dark` | light text on a dark background |
| `navbar-brand` | the big logo/name on the left |
| `navbar-collapse` + `navbar-toggler` | the bit that folds away on small screens |
| `nav-item` / `nav-link` | one row, and the clickable thing in it |

You did not have to learn these. You copied them. That is how you use
Bootstrap — keep a snippet of the shapes you use and paste them.

> **Two errors coming right now.** The Shop link points at
> `{% url 'shop:product_list' %}` and that page does not exist until Guide 07.
> If it throws, either comment those two lines out for now and uncomment them in
> Guide 07, or just carry on — Django only complains when the link is rendered,
> so you will see the error on every page until then. **Commenting them out is
> the tidier option.** The Log in link works, because Django gives you
> `/accounts/login/` for free once you add the auth URLs in Guide 09. Until
> then it will 404 when clicked, which is fine.

---

## Step 4 — Add a footer

At the bottom of `base.html`, after the script tags and before `</body>`:

```html
  <footer class="bg-dark text-secondary py-4 mt-5">
    <div class="container d-flex justify-content-between">
      <small>ByteBarn — a practice shop, built for learning.</small>
      <small>Not a real shop. No real money.</small>
    </div>
  </footer>
```

**Checkpoint.** A dark bar at the bottom of the page with small grey text.

---

## Step 5 — Add flash messages

"Flash messages" are the green or red strips that say *"Added to basket"* or
*"Your password is wrong"*. They are stored for exactly one page load.

In `base.html`, directly **after** `</nav>` and **before** `<main>`:

```html
  <!-- ================= FLASH MESSAGES ================= -->
  {% if messages %}
    <div class="container pt-3">
      {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
          {{ message }}
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
      {% endfor %}
    </div>
  {% endif %}
```

| Tag | What it does |
|-----|--------------|
| `{% if messages %}` | only show this if there are any |
| `{% for message in messages %}` | repeat for each one |
| `{{ message }}` | print the text |
| `alert-{{ message.tags }}` | pick green for success, red for error |

**Checkpoint.** Nothing changes — there are no messages yet.

**Test it.** In `shop/views.py`:

```python
from django.contrib import messages
from django.shortcuts import render


def home(request):
    """The landing page."""
    messages.success(request, "Hello from Django!")
    return render(request, "shop/home.html")
```

Save, refresh.

**Checkpoint.** A green strip under the navbar saying *Hello from Django!*,
with an × to dismiss it.

Refresh again — it is gone. **That is the point of a flash message**: it appears
once. Now delete the `messages.success(...)` line and keep the rest.

> The messages block belongs in `base.html`, once. Putting it in every page is
> the sort of repetition base templates exist to stop.

---

## Step 6 — Add the sticky navbar and a background

Add `sticky-top` to the nav and `bg-body-tertiary` to the body:

```html
<nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top">
```

```html
<body class="bg-body-tertiary">
```

**Checkpoint.** The navbar stays put when you scroll, and the page has a faint
grey background so white cards stand out.

---

## Step 7 — A second page, to prove the point

Add to `shop/views.py`:

```python
def test_page(request):
    """A throwaway page, here to prove base.html is being reused."""
    return render(request, "shop/test_page.html")
```

Add to `shop/urls.py`:

```python
    path("test-page/", views.test_page, name="test_page"),
```

Create `templates/shop/test_page.html`:

```html
{% extends "base.html" %}

{% block title %}Test page — ByteBarn{% endblock %}

{% block content %}
  <h1>Test page</h1>
  <p>Same navbar, same footer, completely different content.</p>
{% endblock %}
```

**Checkpoint.** <http://127.0.0.1:8000/test-page/> has the identical navbar and
footer, and different content in the middle. We wrote a whole page in nine lines
and did not repeat a single line of HTML.

Add a link to it in the navbar if you want, or delete the view, the URL and the
template — you have proved what you needed to.

---

## Mission complete

- [ ] `templates/base.html` exists with `title`, `content` and `scripts` blocks
- [ ] `home.html` uses `{% extends %}` and contains no `<html>` or `<head>`
- [ ] There is a dark navbar with a brand, links and a mobile toggle
- [ ] There is a footer
- [ ] Flash messages appear when a view calls `messages.success()`
- [ ] A second page reuses the same navbar and footer
- [ ] You know why `{% extends %}` must come first

**Commit:** `git commit -m "Guide 04: base template and navbar"`

---

## If something goes wrong

**`blocktag on line N: 'extends' must be the first tag in the template`**
Something is above `{% extends %}` — often a comment or a blank line with
content. Move it to the top.

**`Invalid block tag`**
You typed `{% block content %}` without its matching `{% endblock %}`. Blocks must
be closed.

**Content from `home.html` does not appear**
It is outside a `{% block %}`. Everything in a child template must be inside one.

**The navbar does not fold away on a small screen**
`bootstrap.bundle.min.js` is missing or is above `</body>`. It must be the last
thing before `</body>`.

**`NoReverseMatch` for `shop:product_list`**
You have not built that page yet. Comment the link out until Guide 07.

**Flash messages do not appear**
Check the `{% if messages %}` block is directly after `</nav>` and *outside* any
`{% block %}` in base.html. Also check `django.contrib.messages` is in
`INSTALLED_APPS` and `django.contrib.messages.context_processors.messages` is in
`TEMPLATES["OPTIONS"]["context_processors"]` — Guide 02's default settings
already have both.

**Two navbars**
Your `home.html` still has its old navbar in it. Delete everything that now
lives in `base.html`.

---

Next: [05 — The Product model and admin](05-products-model-and-admin.md)