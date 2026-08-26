# 🐾 PocketPaws

PocketPaws is a desktop-based virtual pet simulation game. Players can adopt a pet, monitor its real-time vitals, and manage an in-game economy to purchase food, toys, and medicine. 

## ✨ Features
* **Pet Care Mechanics:** Monitor and maintain your pet's Health, Hunger, Happiness, and Energy levels. 
* **In-Game Economy & Shop:** Earn coins to purchase items from the shop.
* **Inventory Management:** Store and use items to keep your pet happy and healthy.
* **Persistent Save Data:** Automatically saves your pet's progress and inventory locally so you never lose your data.
* **Admin Control Panel:** Built-in administrative tools for database and user management.

## 🛠️ Tech Stack
* **Language:** Python 3
* **GUI Framework:** Tkinter
* **Database:** SQLite3
* **Image Processing:** Pillow (PIL)
* **Executable Packaging:** PyInstaller

## 🎮 How to Play
You don't need to install Python to play! 
1. Navigate to the [Releases](../../releases) tab on this repository.
2. Download the latest `PocketPaws.exe` file.
3. Run the executable. 
> *Note: If Windows SmartScreen flags the executable as unrecognized, simply click **More info** -> **Run anyway**.*

### Where is my save data?
PocketPaws automatically generates a safe, permanent SQLite database file on your computer the first time you open it. You can find your save data here:
* **Windows:** `C:\Users\YourName\PocketPaws\pet_simulator.db`
* **Mac/Linux:** `~/PocketPaws/pet_simulator.db`

### 💾 Permanent Save Data
PocketPaws acts like a true desktop application. The first time you open the game, it automatically generates a permanent, safe folder on your computer to store your SQLite database. 

**Your pet's progress, items, and coins are saved permanently, even if you delete or update the `.exe` file!**

You can find or back up your save data here:
* **Windows:** `C:\Users\YourName\PocketPaws\pet_simulator.db`
* **Mac/Linux:** `~/PocketPaws/pet_simulator.db`