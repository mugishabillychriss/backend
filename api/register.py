# api/register.py
import os
import json
import psycopg2
from werkzeug.security import generate_password_hash

def handler(request):

    # ✅ If browser visits via GET, show a simple HTML form
    if request.method == "GET":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "body": """
                <h1>User Registration</h1>
                <form method="POST">
                  Username: <input name="username" /><br/>
                  Password: <input name="password" type="password" /><br/>
                  <button type="submit">Register</button>
                </form>
            """
        }

    # ✅ Handle POST request for registration
    if request.method == "POST":
        try:
            # Check if request is JSON or form submission
            if "application/json" in request.headers.get("Content-Type", ""):
                data = json.loads(request.body)
            else:
                from urllib.parse import parse_qs
                data = parse_qs(request.body)
                data = {k: v[0] for k, v in data.items()}

            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Missing fields"})
                }

            hashed_password = generate_password_hash(password)

            # Connect to PostgreSQL
            conn = psycopg2.connect(os.environ["DATABASE_URL"])
            cur = conn.cursor()

            # Create table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)

            # Insert new user
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )

            conn.commit()
            cur.close()
            conn.close()

            return {
                "statusCode": 201,
                "headers": {"Content-Type": "text/html"},
                "body": "<h2>User registered successfully!</h2>"
            }

        except Exception as e:
            return {
                "statusCode": 500,
                "body": f"<h2>Error: {str(e)}</h2>"
            }

    # Any other HTTP method
    return {"statusCode": 405, "body": "Method not allowed"}