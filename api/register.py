import os
import json
import psycopg2
from werkzeug.security import generate_password_hash

def handler(request):

    # Only POST requests allowed
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Method not allowed"})
        }

    try:
        # Parse request body
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing fields"})
            }

        # Hash password
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

        # Insert user
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )

        conn.commit()
        cur.close()
        conn.close()

        return {
            "statusCode": 201,
            "body": json.dumps({"message": "User registered"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
