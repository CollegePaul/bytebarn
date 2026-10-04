# 01 — Set up your environment

**Mission:** install Python, VS Code and Django, in a way that never breaks your machine.
**Time:** about 30 minutes
**You will have when you finish:** a folder, a virtual environment, and Django working.

---

## Before you start

Decide where the project will live. Somewhere like:

```
C:\Users\YourName\Documents\bytebarn
```

Use your own username, obviously. Create that folder now.

---

## Step 1 — Is Python installed?

Press <kbd>Win</kbd>+<kbd>R</kbd>, type `cmd`, press <kbd>Enter</kbd>. You should
see a black window. That is the **command prompt**. You will use it constantly.

Type this and press <kbd>Enter</kbd>:

```bat
py --version
```

**Good** — something like:

```
Python 3.12.7
```

**Also fine:** `python --version`, if that prints 3.10 or newer.

**If you see "'py' is not recognized..."** — Python is not installed, or is not
on your PATH. Go to <https://www.python.org/downloads/> and install it.

> **The one checkbox that matters.** On the first screen of the Python
> installer, tick **"Add python.exe to PATH"** *before* you click *Install*. If
> you miss it, everything below breaks and fixing it is a nuisance.

> **Which version?** Anything from 3.10 up. Django 5 needs 3.10 or newer. Do not
> install Python 2 — if `python --version` says `Python 2.7.x`, install 3 as
> well and always use `py` to call it.

---

## Step 2 — Open cmd in your project folder

**Manual way:** open File Explorer, go to `C:\Users\YourName\Documents`, click
in the **address bar** at the top, type `cmd`, press <kbd>Enter</kbd>. A command
prompt opens right there.

Check where you are:

```bat
cd
```

Now make the project folder and move into it:

```bat
mkdir bytebarn
cd bytebarn
```

---

## Step 3 — Make a virtual environment

```bat
py -m venv .venv
```

This creates a folder called `.venv` inside your project. It holds its own
private copy of Python and, later, its own private copy of Django.

> **Why bother?** Because `pip install django` without a virtual environment
> dumps Django into your one system-wide Python. Do that on a school laptop
> alongside someone else's project and you *will* break something. The `.venv`
> folder means this project's packages live here and nowhere else. Delete it and
> rebuild it whenever you like — nothing outside the project is affected.

It takes about ten seconds and prints nothing when it is done. Silence is
success.

---

## Step 4 — Turn the virtual environment on

```bat
.venv\Scripts\activate
```

**Checkpoint.** Your prompt now starts with `(.venv)`:

```
(.venv) C:\Users\YourName\Documents\bytebarn>
```

If you do not see `(.venv)`, stop and check the command — it must be
`.venv\Scripts\activate`.

> **PowerShell users.** The command is `.venv\Scripts\Activate.ps1`, and if it
> complains about running scripts, run this once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

**Important:** you must do this in **every new command prompt window**. The
prompt looks normal again after you close the window. That is not a bug.

---

## Step 5 — Install Django

```bat
python -m pip install django
```

You will see it downloading and installing several packages, ending with:

```
Successfully installed asgiref-3.8.1 sqlparse-0.5.3
```

(The exact numbers will differ. That is fine.)

Check it:

```bat
python -c "import django; print(django.get_version())"
```

**Checkpoint.** It prints a version number like `5.1.15`.

> **Use `python -m pip`, not bare `pip`.** It guarantees pip belongs to the same
> Python you are running. Bare `pip` sometimes points somewhere else and you end
> up installing into the wrong place.

---

## Step 6 — Open it in VS Code

Download VS Code from <https://code.visualstudio.com/> if you have not got it.

With your command prompt still open in the `bytebarn` folder:

```bat
code .
```

VS Code opens your project. The dot means *"the current folder"*.

If `code` is not recognised, open VS Code manually, choose **File → Open Folder**,
and pick `C:\Users\YourName\Documents\bytebarn`.

### Install the Python extension

Click the Extensions icon on the left (the squares), search for **Python**, and
install the one by Microsoft.

### Point VS Code at your virtual environment

1. Press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>
2. Type **Python: Select Interpreter** and press <kbd>Enter</kbd>
3. Pick the one that looks like `.\.venv\Scripts\python.exe`

**Checkpoint.** The status bar at the bottom left shows something like
`Python 3.12.7 ('.venv': venv)`.

> **Handy trick.** Press <kbd>Ctrl</kbd>+<kbd>`</kbd> to open VS Code's own
> terminal. It opens a command prompt already inside your project — type
> `.venv\Scripts\activate` there and check for `(.venv)`.

---

## Step 7 — Set up Git

Git records your work so you can undo it. You will use it after every guide.

```bat
git --version
```

If that prints a version, you are done. If not, install Git for Windows from
<https://git-scm.com/download/win> and reopen the command prompt.

Tell Git who you are, once:

```bat
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Now create a `.gitignore`. In VS Code, right-click in the file list → **New
File**, name it exactly `.gitignore` (no extension), and paste this in:

```gitignore
# The virtual environment - never commit this, it is huge and disposable
.venv/

# The database - it is generated from migrations, do not commit it
*.sqlite3
db.sqlite3

# Python leftovers
__pycache__/
*.pyc

# Editors
.vscode/
.idea/

# Files your operating system makes
Thumbs.db
.DS_Store
```

Save it, then make your first commit:

```bat
git add .
git commit -m "Start of the ByteBarn project"
```

**Checkpoint.** Something like:

```
[main (root-commit) 1a2b3c4] Start of the ByteBarn project
 1 file changed, 12 insertions(+)
```

---

## Step 8 — Build the habit

From now on, after **every guide**:

```bat
git add .
git commit -m "Guide 04: navbar"
```

`git log --oneline` then shows everything you have done, and
`git checkout .` throws away changes you have not committed.

---

## If something goes wrong

**`'py' is not recognized as an internal or external command`**
Python is not on your PATH. Reinstall it and tick *Add python.exe to PATH*, then
close and reopen the command prompt.

**`The system cannot find the path specified` when activating**
You are not in the project folder. Run `dir` and check you can see `.venv`. If it
is not there, repeat Step 3.

**`'pip' is not recognized`**
Use `python -m pip` instead, as in Step 5.

**`error: externally-managed-environment`**
The virtual environment is not active — look for `(.venv)` at the start of your
prompt, and if it is missing run Step 4 again.

**VS Code shows a red squiggle under every import**
The interpreter is wrong. Redo Select Interpreter, then restart VS Code.

**It all worked, I closed the prompt, and `(.venv)` is gone**
Expected. Turn it back on with Step 4.

---

## Mission complete

- [ ] `py --version` prints Python 3.10 or newer
- [ ] `python -c "import django; print(django.get_version())"` prints a version
- [ ] A `.venv` folder exists in your project
- [ ] VS Code opens your project folder
- [ ] The status bar shows `Python 3.12.7 ('.venv': venv)`
- [ ] `.gitignore` exists and contains `.venv/`
- [ ] You have made at least one git commit

**Commit:** `git commit -m "Guide 01: environment set up"`

---

Next: [02 — Start the Django project](02-start-the-django-project.md)