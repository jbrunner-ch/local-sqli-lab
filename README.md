# Local SQL Injection Test Lab

A lightweight, intentionally vulnerable web application built with **Python (Flask)** and **MySQL 8.0** for **local security testing, SQL injection (SQLi) analysis, and automated scanner verification**.

---

## ⚠️ Security & Network Warnings (Read Before Running)

> **For Local Educational & Security Testing Only**  
> This application is **deliberately insecure**. **Never** deploy it to a public server, cloud environment, or untrusted network.

1. **Intentional SQL Injection Vulnerability:**
   - The `POST /login` endpoint constructs SQL queries via direct string concatenation without prepared statements or input sanitization.
   - Database error messages are returned directly in the HTTP response (`500 Internal Server Error`) to facilitate error-based SQLi testing.
2. **Hardcoded Demo Credentials:**
   - The default MySQL root password (`rootpass`) and application user (`admin` / `SuperGeheim123`) are intentionally weak and hardcoded for local lab setup. Never reuse these credentials elsewhere.
3. **Network Exposure Risks (Even with `localhost` / `127.0.0.1`):**
   - By default, `docker-compose.yml` binds ports to `127.0.0.1`, and `app.py` defaults to `FLASK_HOST=127.0.0.1` when run directly.
   - **However, the application can still become reachable over a network** if:
     - `FLASK_HOST` is changed to `0.0.0.0` outside Docker,
     - port forwarding, SSH tunnels, reverse proxies, or tools like `ngrok` are active,
     - Docker Desktop / WSL / firewall settings expose container ports to the host LAN/WLAN.
   - Only run this lab on a trusted machine, and stop the containers/process when you are done testing.

---

## Project Structure

```text
.
├── app.py                 # Flask backend with automatic DB init & vulnerable /login
├── docker-compose.yml     # MySQL 8.0 + Flask backend (bound to 127.0.0.1)
├── Dockerfile             # Python 3.12 image for the Flask backend
├── requirements.txt       # Python dependencies (Flask, mysql-connector-python)
├── static/
│   └── index.html         # Simple login form (POST /login)
├── Guide.pdf              # Detailed printable PDF guide
└── README.md              # Project documentation
```

---

## Prerequisites

- **Option A (Recommended):** [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose).
- **Option B (Without Docker):** Python 3.10+ and a locally running MySQL 8.0 server on `127.0.0.1:3306`.

---

## Quick Start

### Option A: Using Docker Compose (Recommended)

1. **Clone the repository** and enter the project directory:
   ```bash
   git clone https://github.com/jbrunner-ch/Testwebsite_sql_injection.git
   cd Testwebsite_sql_injection
   ```
2. **Build and start the containers:**
   ```bash
   docker compose up --build
   ```
3. **Wait for initialization:**  
   The backend automatically retries connecting to MySQL until it finishes booting, then creates the database `testdb_sql_injection`, the `users` table, and the test account (`admin` / `SuperGeheim123`). Once you see:
   ```text
   Datenbank erfolgreich initialisiert.
   * Running on http://127.0.0.1:5000
   ```
   the app is ready.
4. **Open in your browser:**  
   `http://127.0.0.1:5000`
5. **Stop or reset:**
   - Stop containers: press `Ctrl+C` or run `docker compose down`
   - Stop and wipe the MySQL data volume: `docker compose down -v`

---

### Option B: Running Directly Without Docker

If you already have MySQL running locally (e.g., MySQL Community Server or XAMPP):

1. **Install Python dependencies:**
   - Windows:
     ```powershell
     py -m pip install -r requirements.txt
     ```
   - macOS / Linux:
     ```bash
     pip3 install -r requirements.txt
     ```

2. **Set environment variables and start `app.py`:**  
   *(Replace `YOUR_MYSQL_PASSWORD` with your local MySQL `root` password, or `""` if none is set.)*

   - **Windows (PowerShell):**
     ```powershell
     $env:DB_HOST="127.0.0.1"
     $env:DB_USER="root"
     $env:DB_PASSWORD="YOUR_MYSQL_PASSWORD"
     py app.py
     ```
   - **Windows (CMD):**
     ```cmd
     set DB_HOST=127.0.0.1
     set DB_USER=root
     set DB_PASSWORD=YOUR_MYSQL_PASSWORD
     py app.py
     ```
   - **macOS / Linux:**
     ```bash
     DB_HOST=127.0.0.1 DB_USER=root DB_PASSWORD=YOUR_MYSQL_PASSWORD python3 app.py
     ```

3. **Open in your browser:**  
   `http://127.0.0.1:5000`

---

## Configuration (Environment Variables)

| Variable | Default (`app.py`) | Docker Compose Value | Description |
| :--- | :--- | :--- | :--- |
| `DB_HOST` | `db` | `db` | MySQL hostname (`127.0.0.1` when running without Docker) |
| `DB_PORT` | `3306` | `3306` | MySQL port |
| `DB_USER` | `root` | `root` | MySQL username |
| `DB_PASSWORD` | `rootpass` | `rootpass` | MySQL password |
| `DB_NAME` | `testdb_sql_injection` | `testdb_sql_injection` | Target database auto-created on startup |
| `FLASK_HOST` | `127.0.0.1` | `0.0.0.0` | Flask bind address (`127.0.0.1` keeps direct runs local-only) |

---

## Testing & Example Payloads

You can test the application via the web form at `http://127.0.0.1:5000` or with `curl`:

| Test Case | `username` | `password` | Expected Result |
| :--- | :--- | :--- | :--- |
| Valid login | `admin` | `SuperGeheim123` | `Congrats!` page (`HTTP 200`) |
| Invalid credentials | `admin` | `wrongpass` | Login failed message (`HTTP 401`) |
| Auth bypass (SQLi) | `' OR '1'='1` | *(anything)* | `Congrats!` page (`HTTP 200`) |
| Comment bypass (SQLi) | `admin' -- ` | *(anything)* | `Congrats!` page (`HTTP 200`) |
| Error-based SQLi | `'` | *(anything)* | Raw MySQL syntax error (`HTTP 500`) |

### `curl` Examples

```bash
# Valid login
curl -i -X POST http://127.0.0.1:5000/login -d "username=admin&password=SuperGeheim123"

# SQL injection bypass
curl -i -X POST http://127.0.0.1:5000/login -d "username=' OR '1'='1&password=x"

# Trigger MySQL syntax error
curl -i -X POST http://127.0.0.1:5000/login -d "username='&password=x"
```

---

## Troubleshooting

- **`pip` is not recognized on Windows:** Use `py -m pip install -r requirements.txt` and `py app.py`, or reinstall Python with **"Add python.exe to PATH"** checked.
- **`Access denied for user 'root'@'localhost'`:** Your local MySQL uses a different password than `rootpass`. Set `$env:DB_PASSWORD="YOUR_PASSWORD"` before running `py app.py`.
- **`Unknown MySQL server host 'db'`:** You ran `app.py` directly without setting `$env:DB_HOST="127.0.0.1"`.
- **Port `3306` or `5000` already in use:** Stop any conflicting local MySQL/web service or adjust the left side of the port mapping in `docker-compose.yml`.
