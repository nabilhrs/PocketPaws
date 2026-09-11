# 🐾 PocketPaws

A desktop virtual pet simulator built with Python and Tkinter. Adopt a pet, keep its vitals up
in real time, earn coins, and spend them in the shop on food, toys and medicine — your pet keeps
living (and getting hungry) even while the game is closed.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-3776AB)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)

**[⬇️ Download the latest PocketPaws.exe](../../releases/latest)** — no Python install needed.

## ✨ Features

- **Pet care in real time** — Health, Hunger, Happiness and Energy decay over time, including
  while the game is closed (offline, time-based stat decay).
- **In-game economy** — earn coins and buy food, toys, medicine, energy items and charms in the shop.
- **Inventory** — store items and use them on your pet when it needs them.
- **Multiple species** — Dog, Cat and Rabbit out of the box, each with its own decay rates; admins
  can add new species.
- **Pet memorial** — pets that pass away are remembered in a memorial view.
- **User and admin portals** — players register their own accounts; admins manage users and species.
- **Persistent save data** — progress is saved automatically to a local SQLite database.

## 🛠️ Tech stack

| Area | Technology |
|---|---|
| Language | Python 3 |
| GUI | Tkinter |
| Database | SQLite3 |
| Images / audio | Pillow, pygame |
| Packaging | PyInstaller |

## 🧱 Architecture

The app follows an MVC-style split:

```
main.py              Entry point — initialises the database and opens the login screen
database.py          Schema, seed data and migrations (SQLite)
models/              Pet and item classes (OOP, inheritance per species/item type)
templates/           Tkinter layouts for each screen (the "view" layer)
views/               Screen logic — handles input and talks to the database (the "controller" layer)
controllers/         Decay engine for time-based stat decay
utils/               Password hashing (security.py) and sound playback
assets/              Images and sounds
```

Passwords are stored as salted PBKDF2-SHA256 hashes (`utils/security.py`). Accounts from older
versions that used plain SHA-256 are upgraded automatically on their next login.

## ▶️ Run from source

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Creating an admin

There is no built-in admin account. Create one with:

```bash
python make_admin.py
```

You'll be prompted for a username and password. Alternatively, set the
`POCKETPAWS_ADMIN_PASSWORD` environment variable before the first launch and an `admin`
account will be created with that password.

## 💾 Save data

The first time PocketPaws runs, it creates a permanent save file outside the app folder, so your
pet's progress, items and coins survive even if you delete or update the `.exe`:

- **Windows:** `C:\Users\<YourName>\PocketPaws\pet_simulator.db`
- **macOS/Linux:** `~/PocketPaws/pet_simulator.db`

Back up that file to keep your save.

> **Windows SmartScreen:** the `.exe` isn't code-signed, so SmartScreen may flag it as
> unrecognised. Click **More info → Run anyway**.
