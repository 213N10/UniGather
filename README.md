
# UniGather  
# 🚀 UniGather App: Local Launch and Testing Guide

This guide outlines the steps required to run and test the **UniGather** application locally. Follow the instructions below.

---

## 1. 🛠️ Database Setup (PostgreSQL)

The application uses a PostgreSQL database.

### Steps:

#### 🔸 Install PostgreSQL  
Download and install PostgreSQL for your operating system:  
👉 [https://www.postgresql.org/download/](https://www.postgresql.org/download/)

#### 🔸 Create the `postgres` user and set the password

In your terminal or pgAdmin, execute the following commands (you may need superuser privileges):

```sql
CREATE USER postgres WITH PASSWORD '0000';
ALTER USER postgres WITH SUPERUSER;
```

#### 🔸 Create the `uni_gather` database

```sql
CREATE DATABASE uni_gather OWNER postgres;
```

#### 🔸 Run the SQL script

Navigate to the directory containing the `uniGather.sql` file and run:

```bash
psql -U postgres -d uni_gather -f uniGather.sql
```

---

## 2. ⚙️ Backend Setup (FastAPI)

The backend of the application uses the **FastAPI** framework.

### Steps:

#### 🔸 Navigate to the backend folder:

```bash
cd unigather_backend
```

#### 🔸 Install Python dependencies:

```bash
pip install -r requirements.txt
```

#### 🔸 Start the backend server:

```bash
fastapi dev main.py
```

The backend should be available at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 3. 📱 Frontend Setup (Flutter)

The frontend is a Flutter application.

### Steps:

#### 🔸 Install Flutter

👉 [Official Flutter installation guide](https://flutter.dev/docs/get-started/install)

#### 🔸 Set up Android emulator

1. Install **Android Studio**.  
2. Open **Device Manager** (or **AVD Manager**).  
3. Create a new virtual device (recommended: **Pixel 5**).  
4. Launch the emulator.

#### 🔸 Navigate to the frontend folder:

```bash
cd unigather_frontend
```

#### 🔸 Run the Flutter app:

```bash
flutter run
```

This will build and install the app on the emulator. The first launch may take a few minutes.

---

## 4. 📦 Additional Dependencies

During `flutter run` or `pip install`, you may encounter messages about missing packages or SDK components. Follow the tools’ instructions to install any missing dependencies.

---

## 5. ✅ Verification

If both the backend (FastAPI) and frontend (Flutter) are running properly:

- The UniGather app should appear on the Pixel 5 emulator.
- You can begin testing the app functionality.
