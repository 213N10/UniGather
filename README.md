# UniGather
# 🚀 UniGather App: Local Launch and Testing Guide

Ten przewodnik opisuje kroki potrzebne do lokalnego uruchomienia i testowania aplikacji **UniGather**. Postępuj zgodnie z instrukcjami poniżej.

---

## 1. 🛠️ Konfiguracja bazy danych (PostgreSQL)

Aplikacja korzysta z bazy danych PostgreSQL.

### Kroki:

#### 🔸 Zainstaluj PostgreSQL
Pobierz i zainstaluj PostgreSQL dla swojego systemu operacyjnego:  
👉 [https://www.postgresql.org/download/](https://www.postgresql.org/download/)

#### 🔸 Utwórz użytkownika `postgres` i ustaw hasło

W terminalu lub narzędziu pgAdmin wykonaj następujące polecenia (może być wymagane połączenie jako superużytkownik):

```sql
CREATE USER postgres WITH PASSWORD '0000';
ALTER USER postgres WITH SUPERUSER;
```

#### 🔸 Utwórz bazę danych `uni_gather`

```sql
CREATE DATABASE uni_gather OWNER postgres;
```

#### 🔸 Uruchom skrypt SQL

Przejdź do katalogu zawierającego plik `uniGather.sql` i uruchom:

```bash
psql -U postgres -d uni_gather -f uniGather.sql
```

---

## 2. ⚙️ Konfiguracja backendu (FastAPI)

Backend aplikacji działa na frameworku **FastAPI**.

### Kroki:

#### 🔸 Przejdź do folderu backendu:

```bash
cd unigather_backend
```

#### 🔸 Zainstaluj zależności Pythona:

```bash
pip install -r requirements.txt
```

#### 🔸 Uruchom serwer backendu:

```bash
fastapi dev main.py
```

Backend powinien być dostępny pod adresem: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 3. 📱 Konfiguracja frontendu (Flutter)

Frontend to aplikacja Flutter.

### Kroki:

#### 🔸 Zainstaluj Flutter

👉 [Oficjalna instrukcja instalacji Fluttera](https://flutter.dev/docs/get-started/install)

#### 🔸 Skonfiguruj emulator Androida

1. Zainstaluj **Android Studio**.
2. Otwórz **Device Manager** (lub **AVD Manager**).
3. Utwórz nowe urządzenie wirtualne (rekomendowany: **Pixel 5**).
4. Uruchom emulator.

#### 🔸 Przejdź do folderu frontendu:

```bash
cd unigather_frontend
```

#### 🔸 Uruchom aplikację Flutter:

```bash
flutter run
```

To zbuduje aplikację i zainstaluje ją na emulatorze. Pierwsze uruchomienie może potrwać kilka minut.

---

## 4. 📦 Dodatkowe zależności

Podczas `flutter run` lub `pip install` mogą pojawić się komunikaty o brakujących pakietach lub komponentach SDK. Postępuj zgodnie z instrukcjami narzędzi, aby zainstalować brakujące zależności.

---

## 5. ✅ Weryfikacja

Jeśli backend (FastAPI) i frontend (Flutter) są poprawnie uruchomione:

- Na emulatorze Pixel 5 powinna pojawić się aplikacja UniGather.
- Możesz rozpocząć testowanie działania aplikacji.
