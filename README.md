# 🚗 AutoDrive - Luxury Automotive SaaS & Car Rental Platform

AutoDrive is a modern, high-performance Django web application for luxury vehicle rentals. It features real-time guaranteed fleet availability, custom pick-up/drop-off locations, verified customer reviews & star ratings, digital reservation passes with QR codes, and a comprehensive fleet management console with direct image file uploads.

---

## 💻 PART 1: How to Run on THIS PC (Quick Start)

The environment and database are already prepared on this machine.

### Step 1: Open Terminal / PowerShell
Open your terminal in the project directory:
```powershell
cd "c:\Z\SOU\Semester 3\CRS"
```

### Step 2: (Optional) Seed / Reset Fleet Database
To ensure all vehicles are loaded with the latest INR pricing and demo accounts:
```powershell
python seed_fleet.py
```python -m venv venvpython -m venv venv

### Step 3: Run the Development Server
```powershell
python manage.py runserver
```

### Step 4: Open in Web Browser
Open your browser and navigate to:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

### 🔑 Demo Accounts Available:
- **Driver User Account**:
  - Username: `john_driver`
  - Password: `password123`
- **Fleet Admin Manager Account**:
  - Username: `admin`
  - Password: `admin123`

---

## 🌐 PART 2: How to Run on ANOTHER PC (Setup from Scratch)

Follow these steps to transfer and run this project on any other Windows, Mac, or Linux computer.

### Step 1: Transfer Project Files
Copy the entire project folder (`CRS`) to the new PC via USB flash drive, local network, or zip archive.

---

### Step 2: Install Python
Ensure **Python 3.10** (or higher) is installed on the target PC.
- Download from: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- ⚠️ **Important on Windows**: Check the box **"Add python.exe to PATH"** during installation.

---

### Step 3: Open Terminal in Project Folder
Open Command Prompt, PowerShell, or Terminal on the new PC and navigate to the project directory:
```bash
# Windows Command Prompt / PowerShell
cd path\to\CRS

# Mac / Linux Terminal
cd path/to/CRS
```

---

### Step 4: Create & Activate Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

---

### Step 5: Install Required Python Dependencies
Install Django and Pillow (for handling vehicle image uploads):
```bash
pip install django pillow
```

---

### Step 6: Run Database Migrations
Create the database tables:
```bash
python manage.py migrate
```

---

### Step 7: Seed Initial Fleet Data & Accounts
Run the automated seed script to generate categories, luxury fleet vehicles with INR pricing, and demo user accounts:
```bash
python seed_fleet.py
```

---

### Step 8: Start the Local Development Server
```bash
python manage.py runserver
```

Open your browser at **`http://127.0.0.1:8000/`**.

---

### 📶 Optional: Accessing from Mobile / Other Devices on the Same Wi-Fi Network
To view the website on smartphones or other computers on the same local network:
```bash
python manage.py runserver 0.0.0.0:8000
```
Then find your host PC's IP address (e.g. `ipconfig` on Windows or `ifconfig` on Mac) and access it from mobile via `http://<YOUR_IP>:8000/`.

---

## ⭐ Key Features Summary

1. **Cars & Fleet Catalog**: Filter vehicles by category, powertrain, search terms, and horsepower/price sorting.
2. **Side-by-Side Vehicle Comparison Matrix**: Compare specifications, 0-60mph acceleration, top speed, seating, and rates.
3. **Instant Reservations**:
   - Custom Pick-Up & Drop-Off text locations (e.g. Airports, Hotels, Executive Hubs).
   - Real-time rate calculation (`Daily Rate × Rental Days`).
4. **Verified Customer Reviews**: Rate and review vehicles with interactive 5-star ratings.
5. **Digital Pass & Printable Voucher**: View confirmed reservation receipts with QR codes on *My Bookings*.
6. **Admin Fleet Management**:
   - Add new fleet vehicles directly from the *Cars/Fleet* tab with direct **image file uploads**.
   - Admin Overview Dashboard for tracking fleet revenue and active reservations.
