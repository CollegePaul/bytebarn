# Setting up ByteBarn from scratch

If you are starting from a fresh copy of the project and want the working site
in about two minutes, this is the short version.

## Windows (command prompt)

```bat
cd bytebarn

py -m venv .venv
.venv\Scripts\activate

python -m pip install -r requirements.txt

python manage.py migrate
python manage.py seed_shop
python manage.py createsuperuser

python manage.py runserver
```

Then open <http://127.0.0.1:8000/>.

You will be asked three questions when creating the superuser:

```
Username: shopadmin
Email address: shop@example.com
Password: <something you will remember>
```

## macOS / Linux

Identical, except the activation line:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_shop
python manage.py createsuperuser
python manage.py runserver
```

## What each command does

| Command | Why |
|---------|-----|
| `python -m venv .venv` | makes a private Python for this project |
| `.venv\Scripts\activate` | switches you into it — do this in every new terminal |
| `pip install -r requirements.txt` | installs Django and crispy-forms |
| `manage.py migrate` | builds `db.sqlite3` from the migrations |
| `manage.py seed_shop` | fills the shop with twelve products |
| `manage.py createsuperuser` | makes the staff account for `/admin/` |
| `manage.py runserver` | starts the site on <http://127.0.0.1:8000/> |

## Accounts already in the demo database

The `db.sqlite3` in this repository is a **demo** copy, so you can look at a site
with data in it. Its accounts are:

| Username | Password | What it is |
|----------|----------|------------|
| `shopadmin` | `admin12345` | Superuser — can use `/admin/` |
| `sam` | `testpassword123` | Customer with three orders already placed |

**Delete `db.sqlite3` and run `migrate` + `seed_shop` again** to get a clean
database with no accounts. Then create your own superuser.

## Is it working?

```bat
python manage.py check
```
```
System check identified no issues (0 silenced).
```

```bat
python manage.py test
```
```
Ran 23 tests in 1.7s

OK
```

If both of those are happy and <http://127.0.0.1:8000/> loads, the project is
working.

---

For everything else, start at [docs/00-start-here.md](docs/00-start-here.md).