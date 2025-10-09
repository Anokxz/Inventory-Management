"""Database initialization utilities.

This module provides helpers to ensure the database exists, the application
schema is created, and a default admin user is present. Intended for dev use.
"""
from typing import Dict
import mysql.connector
from werkzeug.security import generate_password_hash


def ensure_database_exists(dbconf: Dict, database_name: str) -> None:
    conf_no_db = dbconf.copy()
    conf_no_db.pop("database", None)
    try:
        tmp_conn = mysql.connector.connect(**conf_no_db)
        tmp_cursor = tmp_conn.cursor()
        create_sql = (
            f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 "
            "COLLATE utf8mb4_unicode_ci;"
        )
        tmp_cursor.execute(create_sql)
        tmp_conn.commit()
        tmp_cursor.close()
        tmp_conn.close()
        print(f"Ensured database exists: {database_name}")
    except mysql.connector.Error as e:
        print(f"Warning: could not ensure database '{database_name}' exists: {e}")


def ensure_schema(dbconf: Dict) -> None:
    try:
        conn = mysql.connector.connect(**dbconf)
        cur = conn.cursor()

        # materials
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS materials (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                quantity INT DEFAULT 0,
                `type` VARCHAR(100)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # products
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                PID INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                category VARCHAR(100),
                psize VARCHAR(100),
                Price DECIMAL(12,2) DEFAULT 0.00,
                InStockCount INT DEFAULT 0,
                Descript TEXT,
                Img LONGBLOB
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # transactions
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_name VARCHAR(255),
                customer_email VARCHAR(255),
                customer_phone VARCHAR(50),
                grand_total DECIMAL(14,2) DEFAULT 0.00,
                invoice VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # transaction_products
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS transaction_products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                transaction_id INT,
                product_name VARCHAR(255),
                quantity INT,
                price_per_unit DECIMAL(12,2),
                total DECIMAL(14,2),
                FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # customizations
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS customizations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT,
                name VARCHAR(255),
                length VARCHAR(100),
                width VARCHAR(100),
                height VARCHAR(100),
                material VARCHAR(100),
                description TEXT,
                status VARCHAR(50) DEFAULT 'pending'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        conn.commit()
        cur.close()
        conn.close()
        print("Ensured DB schema tables exist")
    except mysql.connector.Error as e:
        print(f"Warning: could not ensure DB schema: {e}")


def ensure_user_table_and_admin(dbconf: Dict, username: str = "admin", password: str = "admin") -> None:
    try:
        conn = mysql.connector.connect(**dbconf)
        cur = conn.cursor()
        create_table_sql = (
            "CREATE TABLE IF NOT EXISTS users ("
            "userID INT AUTO_INCREMENT PRIMARY KEY, "
            "username VARCHAR(150) NOT NULL UNIQUE, "
            "password VARCHAR(255) NOT NULL"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
        )
        cur.execute(create_table_sql)
        cur.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        count = cur.fetchone()[0]
        if count == 0:
            hashed = generate_password_hash(password)
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed))
            print(f"Created default user '{username}'")
        conn.commit()
        cur.close()
        conn.close()
    except mysql.connector.Error as e:
        print(f"Warning: could not ensure users table or admin user exists: {e}")


def ensure_all(dbconf: Dict, database_name: str) -> None:
    """Run all ensures in the right order."""
    ensure_database_exists(dbconf, database_name)
    # ensure_schema and ensure_user_table_and_admin expect dbconf to include the database
    ensure_schema(dbconf)
    ensure_user_table_and_admin(dbconf)
"""Database initialization utilities.
This module provides helpers to ensure the database exists, the application
schema is created, and a default admin user is present. Intended for dev use.
"""
from typing import Dict
import mysql.connector
from werkzeug.security import generate_password_hash


def ensure_database_exists(dbconf: Dict, database_name: str) -> None:
    conf_no_db = dbconf.copy()
    conf_no_db.pop("database", None)
    try:
        tmp_conn = mysql.connector.connect(**conf_no_db)
        tmp_cursor = tmp_conn.cursor()
        create_sql = (
            f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 "
            "COLLATE utf8mb4_unicode_ci;"
        )
        tmp_cursor.execute(create_sql)
        tmp_conn.commit()
        tmp_cursor.close()
        tmp_conn.close()
        print(f"Ensured database exists: {database_name}")
    except mysql.connector.Error as e:
        print(f"Warning: could not ensure database '{database_name}' exists: {e}")


def ensure_schema(dbconf: Dict) -> None:
    try:
        conn = mysql.connector.connect(**dbconf)
        cur = conn.cursor()

        # materials
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS materials (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                quantity INT DEFAULT 0,
                `type` VARCHAR(100)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # products
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                PID INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                category VARCHAR(100),
                psize VARCHAR(100),
                Price DECIMAL(12,2) DEFAULT 0.00,
                InStockCount INT DEFAULT 0,
                Descript TEXT,
                Img LONGBLOB
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # transactions
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_name VARCHAR(255),
                customer_email VARCHAR(255),
                customer_phone VARCHAR(50),
                grand_total DECIMAL(14,2) DEFAULT 0.00,
                invoice VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # transaction_products
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS transaction_products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                transaction_id INT,
                product_name VARCHAR(255),
                quantity INT,
                price_per_unit DECIMAL(12,2),
                total DECIMAL(14,2),
                FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        # customizations
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS customizations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT,
                name VARCHAR(255),
                length VARCHAR(100),
                width VARCHAR(100),
                height VARCHAR(100),
                material VARCHAR(100),
                description TEXT,
                status VARCHAR(50) DEFAULT 'pending'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )

        conn.commit()
        cur.close()
        conn.close()
        print("Ensured DB schema tables exist")
    except mysql.connector.Error as e:
        print(f"Warning: could not ensure DB schema: {e}")


def ensure_user_table_and_admin(dbconf: Dict, username: str = "admin", password: str = "admin") -> None:
    try:
        conn = mysql.connector.connect(**dbconf)
        cur = conn.cursor()
        create_table_sql = (
            "CREATE TABLE IF NOT EXISTS users ("
            "userID INT AUTO_INCREMENT PRIMARY KEY, "
            "username VARCHAR(150) NOT NULL UNIQUE, "
            "password VARCHAR(255) NOT NULL"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
        )
        cur.execute(create_table_sql)
        cur.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        count = cur.fetchone()[0]
        if count == 0:
            hashed = generate_password_hash(password)
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed))
            print(f"Created default user '{username}'")
        conn.commit()
        cur.close()
        conn.close()
    except mysql.connector.Error as e:
        print(f"Warning: could not ensure users table or admin user exists: {e}")


def ensure_all(dbconf: Dict, database_name: str) -> None:
    """Run all ensures in the right order."""
    ensure_database_exists(dbconf, database_name)
    # ensure_schema and ensure_user_table_and_admin expect dbconf to include the database
    ensure_schema(dbconf)
    ensure_user_table_and_admin(dbconf)

def init_db(dbconf: Dict, database_name: str) -> None:
    """Initialize the database by ensuring it exists, the schema is set up,
    and a default admin user is created.

    Args:
        dbconf (Dict): Database configuration dictionary.
        database_name (str): Name of the database to ensure and use.
    """
    ensure_all(dbconf, database_name)