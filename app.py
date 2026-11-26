import os
import time
from flask import Flask, request, send_from_directory
import mysql.connector
from mysql.connector import Error

app = Flask(__name__, static_folder="static")

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "rootpass")
DB_NAME = os.getenv("DB_NAME", "testdb_sql_injection")


def get_connection(database=None):
    config = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
    }
    if database:
        config["database"] = database
    return mysql.connector.connect(**config)


def init_db(max_retries=30, delay=2):
    """Connects to MySQL with retries and initializes database, table, and test user."""
    for attempt in range(1, max_retries + 1):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
            cursor.execute(f"USE `{DB_NAME}`")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50),
                    password VARCHAR(50)
                )
                """
            )

            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            (count,) = cursor.fetchone()
            if count == 0:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES ('admin', 'SuperGeheim123')"
                )
                conn.commit()

            print("Datenbank erfolgreich initialisiert.", flush=True)
            return
        except Error as err:
            print(
                f"Warte auf MySQL (Versuch {attempt}/{max_retries}): {err}",
                flush=True,
            )
            time.sleep(delay)
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    raise RuntimeError("Konnte nach mehreren Versuchen keine Verbindung zu MySQL herstellen.")


@app.route("/", methods=["GET"])
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/login", methods=["POST"])
def login():
    data = request.form if request.form else (request.get_json(silent=True) or {})
    username = data.get("username", "")
    password = data.get("password", "")

    conn = None
    cursor = None
    try:
        conn = get_connection(database=DB_NAME)
        cursor = conn.cursor(dictionary=True)

        # ABSICHTLICH UNSICHER: Direkte String-Verkettung für lokale SQLi-Tests
        query = (
            f"SELECT * FROM users WHERE username = '{username}' "
            f"AND password = '{password}'"
        )
        print(f"[DEBUG] Executing query: {query}", flush=True)

        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            logged_in_user = rows[0]["username"]
            return (
                f"""
                <!DOCTYPE html>
                <html lang="de">
                <head><meta charset="UTF-8"><title>Erfolg</title></head>
                <body>
                    <h1>Congrats!</h1>
                    <p>Erfolgreich eingeloggt als: <strong>{logged_in_user}</strong></p>
                    <a href="/">Zurück zum Login</a>
                </body>
                </html>
                """,
                200,
            )

        return (
            """
            <!DOCTYPE html>
            <html lang="de">
            <head><meta charset="UTF-8"><title>Login fehlgeschlagen</title></head>
            <body>
                <h1>Login fehlgeschlagen</h1>
                <p>Ungültiger Benutzername oder falsches Passwort.</p>
                <a href="/">Erneut versuchen</a>
            </body>
            </html>
            """,
            401,
        )
    except Error as err:
        return (
            f"""
            <!DOCTYPE html>
            <html lang="de">
            <head><meta charset="UTF-8"><title>SQL-Fehler</title></head>
            <body>
                <h1>Datenbankfehler</h1>
                <pre>{err}</pre>
                <a href="/">Zurück zum Login</a>
            </body>
            </html>
            """,
            500,
        )
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    init_db()
    flask_host = os.getenv("FLASK_HOST", "127.0.0.1")
    app.run(host=flask_host, port=5000)
