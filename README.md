# Lokale SQL-Injection-Testumgebung

Dieses Repository enthält eine kleine, absichtlich verwundbare Web-Applikation (Python/Flask + MySQL 8.0) zur lokalen Analyse von **SQL-Injection-Schwachstellen (SQLi)** und zum Testen von Sicherheitsmechanismen.

---

## ⚠️ Sicherheitshinweise (Bitte vor Nutzung lesen)

> **Ausschließlich für lokale Tests und Lernzwecke!**  
> Diese Anwendung enthält **absichtlich unsicheren Code** und darf **niemals** in Produktivumgebungen oder öffentlich im Internet betrieben werden.

- **Absichtliche SQL-Injection-Schwachstelle:** Der Endpunkt `POST /login` baut SQL-Abfragen per direkter String-Verkettung (ohne Prepared Statements) zusammen und gibt SQL-Fehlermeldungen direkt im HTTP-Response zurück. Ein Angreifer kann dadurch beliebige SQL-Befehle gegen die Testdatenbank ausführen.
- **Hardcodierte Standard-Zugangsdaten:** Das Projekt nutzt bewusst einfache Test-Passwörter (`root` / `rootpass` für MySQL sowie `admin` / `SuperGeheim123` in der Tabelle `users`). Verwende diese Zugangsdaten niemals anderweitig.
- **Netzwerk-Erreichbarkeit trotz `localhost` / `127.0.0.1`:**
  - In der `docker-compose.yml` sind die Ports auf `127.0.0.1` gebunden, und beim direkten Start über `app.py` lauscht Flask standardmäßig auf `127.0.0.1`.
  - **Wichtig:** Sobald `FLASK_HOST=0.0.0.0` gesetzt wird, ein Reverse-Proxy/Port-Forwarding (z. B. SSH-Tunnel, ngrok, Router-Freigabe, Firewall-Ausnahme) aktiv ist oder Container-Netzwerke anders konfiguriert werden, ist die verwundbare Anwendung **auch für andere Geräte im lokalen Netzwerk (WLAN/LAN) oder darüber hinaus erreichbar**.
  - Betreibe die Testumgebung daher nur in vertrauenswürdigen lokalen Netzen und stoppe die Server/Container nach dem Testen wieder.

---

## Schnellstart

### Option 1: Mit Docker Compose (empfohlen)

Voraussetzung: **Docker** und **Docker Compose** sind installiert und gestartet.

```bash
docker compose up --build
```

- Web-App: `http://127.0.0.1:5000`
- MySQL 8.0: `127.0.0.1:3306` (`root` / `rootpass`)

Zum Beenden und Zurücksetzen:

```bash
docker compose down -v
```

### Option 2: Direkt mit lokalem MySQL & Python (ohne Docker)

Voraussetzung: Ein lokaler MySQL-Server läuft auf `127.0.0.1:3306` und Python 3 ist installiert.

```powershell
py -m pip install -r requirements.txt
$env:DB_HOST="127.0.0.1"
$env:DB_USER="root"
$env:DB_PASSWORD="DEIN_MYSQL_PASSWORT"
py app.py
```

---

## Testdaten

Beim ersten Start legt das Backend automatisch die Datenbank `testdb_sql_injection`, die Tabelle `users` und folgenden Test-Benutzer an:

- **Benutzername:** `admin`
- **Passwort:** `SuperGeheim123`

Weitere Details findest du auch in [Anleitung.pdf](./Anleitung.pdf).
