import os
from typing import Optional

import mysql.connector
from mysql.connector import Error


def get_connection() -> Optional[mysql.connector.MySQLConnection]:
    host = os.getenv("MYSQL_HOST")
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    database = os.getenv("MYSQL_DATABASE", "student_marks_app")

    if not host or not user or not password:
        return None

    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )
        return conn
    except Error:
        return None


def ensure_schema() -> bool:
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
              id INT UNSIGNED NOT NULL AUTO_INCREMENT,
              username VARCHAR(100) NOT NULL,
              password_hash CHAR(64) NOT NULL,
              salt CHAR(32) NOT NULL,
              email VARCHAR(255) NULL,
              verified TINYINT(1) NOT NULL DEFAULT 0,
              verify_token VARCHAR(16) NULL,
              created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (id),
              UNIQUE KEY uniq_username (username)
            )
            """
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Error:
        return False


def insert_user(username: str, password_hash: str, salt: str, email: Optional[str] = None, verified: bool = False, verify_token: Optional[str] = None) -> bool:
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password_hash, salt, email, verified, verify_token) VALUES (%s, %s, %s, %s, %s, %s)",
            (username, password_hash, salt, email, 1 if verified else 0, verify_token),
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Error:
        return False


